import logging
import time

import pulsectl

from linux_arctis_manager.constants import (PULSE_CHAT_NODE_NAME,
                                            PULSE_MEDIA_NODE_NAME,
                                            STEELSERIES_VENDOR_ID)

ONLY_PHYSICAL = 1
ONLY_VIRTUAL = 2
ALL_SINKS = 3

class TypedPulseSinkInfo(pulsectl.PulseSinkInfo):
    name: str


class PulseAudioManager:
    _instance: 'PulseAudioManager|None' = None

    @staticmethod
    def get_instance() -> 'PulseAudioManager':
        if PulseAudioManager._instance is None:
            PulseAudioManager._instance = PulseAudioManager()

        return PulseAudioManager._instance

    def __init__(self):
        self.pulse = pulsectl.Pulse('linux-arctis-manager')
        self.logger = logging.getLogger('PulseAudioManager')
    
    def sink_list_wrapper(self) -> list[TypedPulseSinkInfo]:
        retry_attempts = 15

        sinks: list[TypedPulseSinkInfo] = []
        while retry_attempts > 0:
            try:
                sinks = self.pulse.sink_list()
                break
            except Exception as e:
                self.logger.error(f'Error while getting sink list: {e}')
                retry_attempts -= 1
                time.sleep(1)

        sinks: list[TypedPulseSinkInfo] = sinks if type(sinks) is list else [sinks] # pyright: ignore[reportAssignmentType]

        return sinks
    
    def get_arctis_sinks(self, mode: int = ALL_SINKS, vendor_id: int = STEELSERIES_VENDOR_ID, product_id: int|list[int]|None = None) -> list[TypedPulseSinkInfo]:
        sinks = self.sink_list_wrapper()

        def check_prod_id(product_id_attr: str) -> bool:
            if product_id is None:
                return True

            lst = product_id if type(product_id) is list else [product_id]

            return product_id_attr in [f'0x{pid:04x}' for pid in lst]

        physical = [s for s in sinks if s.proplist.get('device.vendor.id', '') == f'0x{vendor_id:04x}' and check_prod_id(s.proplist.get('device.product.id', ''))]
        virtual = [s for s in sinks if s.proplist.get('node.name', '') in (PULSE_MEDIA_NODE_NAME, PULSE_CHAT_NODE_NAME)]

        if mode == ONLY_PHYSICAL:
            sinks = physical
        elif mode == ONLY_VIRTUAL:
            sinks = virtual
        else:
            sinks = physical + virtual

        return sinks

    def create_virtual_sink(self, name: str, description: str, sink_output: str) -> None:
        sink = next((s for s in self.get_arctis_sinks(ONLY_VIRTUAL) if s.proplist.get('node.name', '') == name), None)
        if sink:
            return
        
        self.logger.info(f'Creating virtual sink "{name}" -> "{sink_output}"...')
        escaped_node_description = description.replace(' ', '\\ ')
        self.pulse.module_load(
            'module-null-sink',
            f'sink_name={name} '
            f'sink_properties=node.description="{escaped_node_description}"'
        )

        self.pulse.module_load(
            'module-loopback',
            f'source={name}.monitor '
            f'sink={sink_output} '
            'latency_msec=0'
        )
    
    def remove_virtual_sink(self, name: str) -> None:
        sink = next((s for s in self.get_arctis_sinks(ONLY_VIRTUAL) if s.proplist.get('node.name', '') == name), None)
        if not sink:
            return
        
        self.logger.info(f'Removing virtual sink "{name}"...')
        modules = self.pulse.module_list()
        for module in modules:
            if module.argument and name in module.argument:
                self.pulse.module_unload(module.index)
    
    def wait_for_physical_device(self, vendor_id: int, product_id: int, attempts: int = 10) -> bool:
        vendor_id_hex = f'0x{vendor_id:04x}'
        product_id_hex = f'0x{product_id:04x}'

        while attempts > 0:
            if next((s for s in self.get_arctis_sinks(ONLY_PHYSICAL, vendor_id=vendor_id, product_id=product_id)), None):
                return True

            attempts -= 1
            time.sleep(1)
        
        self.logger.error(f'Failed to find SteelSeries Arctis device {vendor_id:04x}:{product_id:04x} after {attempts} attempts')

        return False

    def redirect_audio(self, output_sink_node_name: str) -> None:
        self.logger.info(f'Redirecting audio to {output_sink_node_name}...')

        sink = next((s for s in self.sink_list_wrapper() if s.proplist.get('node.nick', '') == output_sink_node_name or s.proplist.get('node.name', '') == output_sink_node_name), None)
        if sink is None:
            self.logger.error(f'Failed to find sink {output_sink_node_name} to set it as default')
            return
        self.pulse.default_set(sink)
    
    def get_default_device(self) -> TypedPulseSinkInfo|None:
        server_info = self.pulse.server_info()
        default_sink_name: str|None = getattr(server_info, 'default_sink_name', None)

        if default_sink_name is None:
            return None
        
        sink = next((s for s in self.sink_list_wrapper() if s.proplist.get('node.name', '') == default_sink_name), None)

        return sink

    def set_mix(self, media_mix: int, chat_mix: int):
        if media_mix > 100:
            media_mix = 100
        if chat_mix > 100:
            chat_mix = 100

        sinks = self.get_arctis_sinks(ONLY_VIRTUAL)

        media = next((s for s in sinks if s.proplist.get('node.name', '') == PULSE_MEDIA_NODE_NAME), None)
        chat = next((s for s in sinks if s.proplist.get('node.name', '') == PULSE_CHAT_NODE_NAME), None)

        if media:
            self.pulse.volume_set_all_chans(media, media_mix / 100)
        if chat:
            self.pulse.volume_set_all_chans(chat, chat_mix / 100)

    def sinks_setup(self, device_name: str, vendor_id: int, product_id: int|list[int]|None):
        real_sinks = self.get_arctis_sinks(ONLY_PHYSICAL, vendor_id=vendor_id, product_id=product_id)

        if not real_sinks:
            self.logger.warning('No SteelSeries Arctis sink found.')
            return

        # Arctis 7 exposes separate game (stereo) and chat (mono) interfaces.
        # Route each virtual sink to the matching physical interface.
        game_sink = next((s for s in real_sinks if 'game' in s.name), None) or \
                    next((s for s in real_sinks if 'stereo' in s.name), None)
        chat_sink = next((s for s in real_sinks if 'chat' in s.name), None) or \
                    next((s for s in real_sinks if 'mono' in s.name), None)

        media_output = (game_sink or real_sinks[0]).name
        chat_output = (chat_sink or real_sinks[0]).name

        self.create_virtual_sink(PULSE_MEDIA_NODE_NAME, f'{device_name} Media', media_output)
        self.create_virtual_sink(PULSE_CHAT_NODE_NAME, f'{device_name} Chat', chat_output)

    def sinks_teardown(self):
        self.logger.info('Removing virtual sinks...')

        try:
            self.remove_virtual_sink(PULSE_MEDIA_NODE_NAME)
            self.remove_virtual_sink(PULSE_CHAT_NODE_NAME)
        except Exception as e:
            # PipeWire may already be shutting down; virtual sinks will be
            # cleaned up by PipeWire itself in that case.
            self.logger.warning(f'Could not remove virtual sinks during teardown (PipeWire may be shutting down): {e}')
