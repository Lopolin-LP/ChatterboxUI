# Chatterbox UI
A Simple Wrapper for `chatterbox-tts` to get a UI up and running! Designed to be installed using `uv`.

### If something breaks, please open an issue and notify me! Thank you!

## Installation

1. Download the release source code or whatever. You can also `git clone` this repo
2. Extract Source if it's still an archive
3. Open Terminal in Source Code folder
4. `uv sync` and you're done

Run the App using
```bash
uv run ./app.py
```
And navigate to [127.0.0.1:7860](http://127.0.0.1:7860) to access the interface once the Startup message appears.

## Isn't that just a copy of `gradio_tts_app.py` in the `chatterbox-tts` GitHub Repo?
TL;DR: Yes.

There's a few modifications made here and there, but overall it's a 1:1 copy.

### Real Differences:
- The WebApp launches by default shared. This is undesirable and triggers Windows Defender. It has been unset to use the default, which changes depending on environment. See the [Gradio Docs: Blocks](https://www.gradio.app/main/docs/gradio/blocks).
- Multilingual Support! Adds an option to change the language and loads the according model. Disable it using `?multi=no` in the url.
- Disables Watermarking because it's broken on `uv` and I don't know how to fix it. See [chatterbox#198](https://github.com/resemble-ai/chatterbox/issues/198).

## Notes about terminal outputs
- On first download, there will be things downloaded and nothing is changing on the bar in terminal. This bar indicates the data written to disk, not data stored to memory.