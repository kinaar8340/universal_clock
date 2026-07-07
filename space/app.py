#!/usr/bin/env python3
"""Gradio demo — Universal π Clock · Egg of Life."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

from universal_clock import UniversalPiClock, render_clock_array
from universal_clock.clock import EARTH_DAY_SECONDS
from universal_clock.visualize import DEFAULT_SLICE_LINES

import gradio as gr

GITHUB_URL = "https://github.com/kinaar8340/universal_clock"
HF_SPACE_URL = "https://huggingface.co/spaces/kinaar111/universal_clock"

SLICE_LINE_CHOICES = [10, 35, 70, 175, 350]
PRESET_TICKS = [0, 1000, 5000, 50000, 500000]


def _format_state(clock: UniversalPiClock) -> str:
    lines = [f"Total ticks: {clock.total_ticks:,}"]
    for i in range(1, 8):
        k = clock.gears[i - 1]
        fill = 100.0 * k / 350
        lines.append(f"Gear {i}: k={k:3d}  v≈{clock.value(i):6.2f}  ({fill:5.1f}% filled)")
    return "\n".join(lines)


def _render(
    clock: UniversalPiClock,
    *,
    slice_lines: int,
    show_labels: bool,
    show_hands: bool,
    show_ticks: bool,
) -> tuple:
    image = render_clock_array(
        clock,
        figsize=(9, 9),
        dpi=110,
        show_ticks=show_ticks,
        show_labels=show_labels,
        show_hands=show_hands,
        slice_lines=slice_lines,
        title="",
    )
    return image, _format_state(clock)


def _new_clock() -> UniversalPiClock:
    return UniversalPiClock()


def reset_clock(
    slice_lines: int,
    show_labels: bool,
    show_hands: bool,
    show_ticks: bool,
) -> tuple:
    clock = _new_clock()
    return clock, *_render(
        clock,
        slice_lines=slice_lines,
        show_labels=show_labels,
        show_hands=show_hands,
        show_ticks=show_ticks,
    )


def advance_ticks(
    clock: UniversalPiClock | None,
    ticks: int,
    slice_lines: int,
    show_labels: bool,
    show_hands: bool,
    show_ticks: bool,
) -> tuple:
    if clock is None:
        clock = _new_clock()
    if ticks > 0:
        clock.tick(ticks)
    return clock, *_render(
        clock,
        slice_lines=slice_lines,
        show_labels=show_labels,
        show_hands=show_hands,
        show_ticks=show_ticks,
    )


def enable_realtime(
    clock: UniversalPiClock | None,
    rev_seconds: float,
    speed: float,
    slice_lines: int,
    show_labels: bool,
    show_hands: bool,
    show_ticks: bool,
) -> tuple:
    if clock is None:
        clock = _new_clock()
    clock.set_earth_rate(rev_seconds)
    return (
        clock,
        True,
        speed,
        *_render(
            clock,
            slice_lines=slice_lines,
            show_labels=show_labels,
            show_hands=show_hands,
            show_ticks=show_ticks,
        ),
    )


def disable_realtime(
    clock: UniversalPiClock | None,
    slice_lines: int,
    show_labels: bool,
    show_hands: bool,
    show_ticks: bool,
) -> tuple:
    if clock is None:
        clock = _new_clock()
    return (
        clock,
        False,
        1.0,
        *_render(
            clock,
            slice_lines=slice_lines,
            show_labels=show_labels,
            show_hands=show_hands,
            show_ticks=show_ticks,
        ),
    )


def realtime_tick(
    clock: UniversalPiClock | None,
    running: bool,
    speed: float,
    slice_lines: int,
    show_labels: bool,
    show_hands: bool,
    show_ticks: bool,
) -> tuple:
    if clock is None:
        clock = _new_clock()
    if running and clock.tick_interval is not None:
        clock.tick_realtime(speed_multiplier=max(speed, 0.001))
    return clock, *_render(
        clock,
        slice_lines=slice_lines,
        show_labels=show_labels,
        show_hands=show_hands,
        show_ticks=show_ticks,
    )


def refresh_view(
    clock: UniversalPiClock | None,
    slice_lines: int,
    show_labels: bool,
    show_hands: bool,
    show_ticks: bool,
) -> tuple:
    if clock is None:
        clock = _new_clock()
    return clock, *_render(
        clock,
        slice_lines=slice_lines,
        show_labels=show_labels,
        show_hands=show_hands,
        show_ticks=show_ticks,
    )


THEME = gr.themes.Base(
    primary_hue="orange",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill_dark="#0d1117",
    block_background_fill_dark="#161b22",
    block_border_width="1px",
    block_title_text_weight="600",
    block_padding="6px",
    layout_gap="8px",
)

CUSTOM_CSS = """
html, body {
    height: 100% !important;
    overflow: hidden !important;
}
.gradio-container {
    max-width: 100% !important;
    width: 100% !important;
    height: 100dvh !important;
    overflow: hidden !important;
    padding: 0.35rem 0.75rem 0.25rem !important;
}
.gradio-container > .main,
.gradio-container > .main > .wrap,
.gradio-container .contain {
    height: 100% !important;
    min-height: 0 !important;
    overflow: hidden !important;
}
footer, .footer {
    display: none !important;
}
#app-header {
    flex-shrink: 0;
    margin-bottom: 0 !important;
}
#app-header h1 {
    font-size: 1.15rem !important;
    margin: 0 !important;
    line-height: 1.25 !important;
}
#app-header p {
    font-size: 0.78rem !important;
    margin: 0.1rem 0 0 !important;
    opacity: 0.85;
}
#main-row {
    height: calc(100dvh - 3.6rem) !important;
    max-height: calc(100dvh - 3.6rem) !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    overflow: hidden !important;
    gap: 0.65rem !important;
}
#col-controls, #col-clock, #col-state {
    height: 100% !important;
    overflow: hidden !important;
    min-height: 0 !important;
}
#col-controls {
    display: flex !important;
    flex-direction: column !important;
    padding-right: 0 !important;
}
#controls-scroll {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    padding-right: 0.35rem !important;
    scrollbar-width: thin;
    scrollbar-color: #3d4f5f #161b22;
}
#controls-scroll::-webkit-scrollbar {
    width: 8px;
}
#controls-scroll::-webkit-scrollbar-track {
    background: #161b22;
    border-radius: 4px;
}
#controls-scroll::-webkit-scrollbar-thumb {
    background: #3d4f5f;
    border-radius: 4px;
}
#controls-scroll::-webkit-scrollbar-thumb:hover {
    background: #5a6d7d;
}
#controls-scroll .block {
    margin-bottom: 0.35rem !important;
}
#controls-scroll h3 {
    font-size: 0.9rem !important;
    margin: 0.35rem 0 0.15rem !important;
}
#col-clock {
    display: flex !important;
    flex-direction: column !important;
    justify-content: stretch !important;
    align-items: stretch !important;
    background: #0d1117 !important;
}
#col-clock > .form {
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    margin: 0 !important;
    padding: 0 !important;
}
#clock-viewport {
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 0 !important;
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    background: #0d1117 !important;
}
#clock-viewport > .form,
#clock-viewport > .block,
#clock-viewport .block,
#clock-viewport .wrap,
#clock-viewport .form {
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 0 !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    overflow: hidden !important;
}
#clock-face {
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 0 !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
#clock-face > .wrap,
#clock-face .wrap {
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
#clock-face .icon-button-wrapper,
#clock-face .image-buttons {
    flex: 0 0 auto !important;
}
#clock-face .image-container,
#clock-face .image-frame,
#clock-face .preview,
#clock-face [data-testid="image"],
#clock-face figure {
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 0 !important;
    width: 100% !important;
    max-height: 100% !important;
    aspect-ratio: unset !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
    background: #0d1117 !important;
}
#clock-face img {
    width: 100% !important;
    height: 100% !important;
    max-width: 100% !important;
    max-height: 100% !important;
    object-fit: contain !important;
    object-position: center center !important;
}
#col-state {
    display: flex !important;
    flex-direction: column !important;
}
#gear-state {
    flex: 0 0 auto !important;
    margin-top: 0 !important;
}
#gear-state textarea {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 0.78rem !important;
    line-height: 1.35 !important;
}
"""


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Universal π Clock") as demo:
        gr.Markdown(
            f"""
# Universal π Clock · Egg of Life
Seven-gear cascading π clock — [GitHub]({GITHUB_URL}) · [Space]({HF_SPACE_URL})
            """,
            elem_id="app-header",
        )

        clock_state = gr.State(_new_clock())
        realtime_running = gr.State(False)

        with gr.Row(elem_id="main-row", equal_height=True):
            with gr.Column(scale=4, min_width=260, elem_id="col-controls"):
                with gr.Column(elem_id="controls-scroll"):
                    gr.Markdown("### Controls")
                    ticks = gr.Slider(
                        minimum=0,
                        maximum=500000,
                        value=5000,
                        step=1000,
                        label="Advance ticks (batch)",
                    )
                    with gr.Row():
                        advance_btn = gr.Button("Advance", variant="primary", scale=2)
                        reset_btn = gr.Button("Reset", scale=1)
                    preset = gr.Radio(
                        choices=[str(v) for v in PRESET_TICKS],
                        value="5000",
                        label="Presets",
                    )
                    gr.Markdown("### Real-time")
                    rev_seconds = gr.Slider(
                        minimum=3600,
                        maximum=200000,
                        value=EARTH_DAY_SECONDS,
                        step=3600,
                        label="Gear 1 revolution (s)",
                    )
                    speed = gr.Slider(
                        minimum=1,
                        maximum=10000,
                        value=1000,
                        step=10,
                        label="Speed multiplier",
                    )
                    with gr.Row():
                        start_rt = gr.Button("Start real-time", variant="secondary")
                        stop_rt = gr.Button("Stop real-time")
                    gr.Markdown("### Display")
                    slice_lines = gr.Dropdown(
                        choices=SLICE_LINE_CHOICES,
                        value=DEFAULT_SLICE_LINES,
                        label="Radial slice lines",
                    )
                    show_hands = gr.Checkbox(value=True, label="Hand indicators")
                    show_labels = gr.Checkbox(value=True, label="k/π labels")
                    show_ticks = gr.Checkbox(value=True, label="Slice lines")

            with gr.Column(scale=7, min_width=360, elem_id="col-clock"):
                with gr.Column(elem_id="clock-viewport"):
                    clock_image = gr.Image(
                        elem_id="clock-face",
                        interactive=False,
                        show_label=False,
                        container=False,
                        buttons=["download", "fullscreen"],
                    )

            with gr.Column(scale=3, min_width=220, elem_id="col-state"):
                state_text = gr.Textbox(
                    label="Gear state",
                    elem_id="gear-state",
                    lines=10,
                    max_lines=10,
                    interactive=False,
                )

        timer = gr.Timer(0.15, active=False)

        outputs = [clock_state, clock_image, state_text]
        rt_outputs = [clock_state, realtime_running, speed, clock_image, state_text]
        view_outputs = [clock_state, clock_image, state_text]
        display_inputs = [slice_lines, show_labels, show_hands, show_ticks]

        reset_btn.click(
            reset_clock,
            inputs=display_inputs,
            outputs=outputs,
        ).then(lambda: False, outputs=realtime_running).then(
            lambda: gr.Timer(active=False),
            outputs=timer,
        )

        advance_btn.click(
            advance_ticks,
            inputs=[clock_state, ticks, *display_inputs],
            outputs=outputs,
        )

        preset.change(
            lambda p: int(p),
            inputs=preset,
            outputs=ticks,
        ).then(
            advance_ticks,
            inputs=[clock_state, ticks, *display_inputs],
            outputs=outputs,
        )

        start_rt.click(
            enable_realtime,
            inputs=[clock_state, rev_seconds, speed, *display_inputs],
            outputs=rt_outputs,
        ).then(lambda: gr.Timer(active=True), outputs=timer)

        stop_rt.click(
            disable_realtime,
            inputs=[clock_state, *display_inputs],
            outputs=rt_outputs,
        ).then(lambda: gr.Timer(active=False), outputs=timer)

        for control in (slice_lines, show_hands, show_labels, show_ticks):
            control.change(
                refresh_view,
                inputs=[clock_state, *display_inputs],
                outputs=view_outputs,
            )

        timer.tick(
            realtime_tick,
            inputs=[
                clock_state,
                realtime_running,
                speed,
                *display_inputs,
            ],
            outputs=view_outputs,
            show_progress="hidden",
        )

        demo.load(
            reset_clock,
            inputs=display_inputs,
            outputs=outputs,
        )

    return demo


if __name__ == "__main__":
    build_demo().launch(theme=THEME, css=CUSTOM_CSS)