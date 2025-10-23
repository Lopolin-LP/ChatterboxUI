from . import chatterbox_patch_eng as cbpeng
from . import chatterbox_patch_mlt as cbmlt
    
def cbpatchinit():
    cbmlt.ChatterboxMultilingualTTS.from_local = cbmlt.cbmtl_from_local_patch
    cbmlt.ChatterboxMultilingualTTS.__init__ = cbmlt.cbmtl___init___patch
    cbpeng.ChatterboxTTS.__init__ = cbpeng.cbeng___init___patch