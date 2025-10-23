import random
import numpy as np
import torch
import gradio as gr
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import gc
from chatterbox_patch import cbpatchinit # Nothing else needs to be done, it only needs to exist

cbpatchinit()

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
available_languages = dict([['English', 'en']])
available_languages_list = list('English')

def swap_key_an_value(dict_in: dict[str, str]):
    return dict(([value, key] for key, value in dict_in.items()))

# General Functions

def set_seed(seed: int):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)

def aggressive_cleanup():
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def get_string_bool(input: str):
    if type(input) == str:
        match input.lower():
            case "yes":
                return True
            case "true":
                return True
            case "no":
                return False
            case "false":
                return False
    return None

# Define available Models (two)
model_mlt_state = gr.State(None, delete_callback=aggressive_cleanup)
model_eng_state = gr.State(None, delete_callback=aggressive_cleanup)

def load_model(language_chooser: gr.Dropdown, request: gr.Request): # .load() auto-appends request to the end (not key based)
    global model_mlt_state, model_eng_state
    multi = get_string_bool(request.request.query_params.get('multi'))
    if multi == None:
        multi = True
    print('Switched to Multilingual' if multi else "Switched to Monolingual (English)")
    aggressive_cleanup()
    if multi == True: # If multi is supposed to be loaded
        if model_mlt_state.value == None: # If no Model has been loaded yet
            model = ChatterboxMultilingualTTS.from_pretrained(DEVICE)
            model_mlt_state.value = model
        else: # Otherwise just use the in-memory model
            model = model_mlt_state.value
    elif multi == False: # Same thing here
        if model_eng_state.value == None:
            model = ChatterboxTTS.from_pretrained(DEVICE)
            model_eng_state.value = model
        else:
            model = model_eng_state
    aggressive_cleanup()
    
    # Update Languages
    global available_languages, available_languages_list
    try: 
        available_languages = swap_key_an_value(model.get_supported_languages())
    except AttributeError:
        available_languages = dict([['English', 'en']])
    available_languages_list = available_languages.keys()
    language_chooser = gr.Dropdown(available_languages_list, label='Language of Text')

    # Return
    return [model, language_chooser]

def generate(model: ChatterboxMultilingualTTS | ChatterboxTTS, text, audio_prompt_path, exaggeration, temperature, seed_num, cfgw, min_p, top_p, repetition_penalty, language_id='English'):
    # if model is None:
    #     model = ChatterboxTTS.from_pretrained(DEVICE)

    # TODO: Put inputs into array and add language_id when Multilingual is detected

    if seed_num != 0:
        set_seed(int(seed_num))
    
    parameters = dict(
        text=text,
        audio_prompt_path=audio_prompt_path,
        exaggeration=exaggeration,
        temperature=temperature,
        cfg_weight=cfgw,
        min_p=min_p,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
    )

    if isinstance(model, ChatterboxMultilingualTTS):
        print(language_id)
        parameters['language_id'] = available_languages[language_id]

    wav = model.generate(**parameters)
    return (model.sr, wav.squeeze(0).numpy())

with gr.Blocks() as demo:
    model_state = gr.State(None, delete_callback=aggressive_cleanup)  # Loaded once per session/user
    # multi_mode = gr.State(True) # Enabled by default; TODO: hotswapping makes memory leak and i'm too lazy to fix it.
    # TODO: Make it URL parameter to disable it just in case.

    with gr.Row():
        with gr.Column():
            text = gr.Textbox(
                value="Now let's make my mum's favourite. So three mars bars into the pan. Then we add the tuna and just stir for a bit, just let the chocolate and fish infuse. A sprinkle of olive oil and some tomato ketchup. Now smell that. Oh boy this is going to be incredible.",
                label="Text to synthesize (max chars 300)",
                max_lines=5
            )
            language_chooser = gr.Dropdown(available_languages, label='Language of Text')

            ref_wav = gr.Audio(sources=["upload", "microphone"], type="filepath", label="Reference Audio File", value=None)
            exaggeration = gr.Slider(0.25, 2, step=.05, label="Exaggeration (Neutral = 0.5, extreme values can be unstable)", value=.5)
            cfg_weight = gr.Slider(0.0, 1, step=.05, label="CFG/Pace", value=0.5)


            with gr.Accordion("More options", open=False):
                seed_num = gr.Number(value=0, label="Random seed (0 for random)")
                temp = gr.Slider(0.05, 5, step=.05, label="temperature", value=.8)
                min_p = gr.Slider(0.00, 1.00, step=0.01, label="min_p || Newer Sampler. Recommend 0.02 > 0.1. Handles Higher Temperatures better. 0.00 Disables", value=0.05)
                top_p = gr.Slider(0.00, 1.00, step=0.01, label="top_p || Original Sampler. 1.0 Disables(recommended). Original 0.8", value=1.00)
                repetition_penalty = gr.Slider(1.00, 2.00, step=0.1, label="repetition_penalty", value=1.2)

            run_btn = gr.Button("Generate", variant="primary")

        with gr.Column():
            audio_output = gr.Audio(label="Output Audio")
            gr.Markdown("""Use `?multi=false` or `?multi=no` to switch from Multilingual to Monolingual (English).""")

    demo.load(fn=load_model, inputs=[language_chooser], outputs=[model_state, language_chooser])

    run_btn.click(
        fn=generate,
        inputs=[
            model_state,
            text,
            ref_wav,
            exaggeration,
            temp,
            seed_num,
            cfg_weight,
            min_p,
            top_p,
            repetition_penalty,
            language_chooser
        ],
        outputs=audio_output,
    )

if __name__ == "__main__":
    demo.queue(
        max_size=1,
        default_concurrency_limit=1,
    ).launch()