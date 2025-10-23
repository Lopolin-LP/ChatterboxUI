from chatterbox.mtl_tts import *
from .perth_fake import *
# from perth.perth_net.perth_net_implicit.perth_watermarker import PerthImplicitWatermarker
# from librosa import resample

# Patch chatterbox mtl_tts
@classmethod
def cbmtl_from_local_patch(cls, ckpt_dir, device) -> 'ChatterboxMultilingualTTS':
    ckpt_dir = Path(ckpt_dir)
    map_location = torch.device(device or "cpu")

    ve = VoiceEncoder()
    ve.load_state_dict(
        torch.load(ckpt_dir / "ve.pt", weights_only=True, map_location=map_location)
    )
    ve.to(device).eval()

    t3 = T3(T3Config.multilingual())
    t3_state = load_safetensors(ckpt_dir / "t3_23lang.safetensors")
    if "model" in t3_state.keys():
        t3_state = t3_state["model"][0]
    t3.load_state_dict(t3_state)
    t3.to(device).eval()

    s3gen = S3Gen()
    s3gen.load_state_dict(
        torch.load(ckpt_dir / "s3gen.pt", weights_only=True, map_location=map_location)
    )
    s3gen.to(device).eval()

    tokenizer = MTLTokenizer(
        str(ckpt_dir / "mtl_tokenizer.json")
    )

    conds = None
    if (builtin_voice := ckpt_dir / "conds.pt").exists():
        conds = Conditionals.load(builtin_voice).to(device)
    
    return cls(t3, s3gen, ve, tokenizer, device, conds=conds)

def cbmtl___init___patch(
        self,
        t3: T3,
        s3gen: S3Gen,
        ve: VoiceEncoder,
        tokenizer: MTLTokenizer,
        device: str,
        conds: Conditionals = None,
    ):
        self.sr = S3GEN_SR  # sample rate of synthesized audio
        self.t3 = t3
        self.s3gen = s3gen
        self.ve = ve
        self.tokenizer = tokenizer
        self.device = device
        self.conds = conds
        self.watermarker = NOTPerthImplicitWatermarker()

# mock.patch.object(ChatterboxMultilingualTTS, 'from_local', cbmtl_from_local_patch)
# Put this in the to be patched script:

