from chatterbox.tts import *
from .perth_fake import *

def cbeng___init___patch(
    self,
    t3: T3,
    s3gen: S3Gen,
    ve: VoiceEncoder,
    tokenizer: EnTokenizer,
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