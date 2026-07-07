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
        show_ticks=show_ticks,
        show_labels=show_labels,
        show_hands=show_hands,
        slice_lines=slice_lines,
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
)

CUSTOM_CSS = """
.gradio-container { max-width: 1180px !important; }
#clock-face { min-height: 520px; }
"""


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Universal π Clock") as demo:
        gr.Markdown(
            f"""
# Universal π Clock · Egg of Life
Seven-gear cascading π clock — sacred geometry timekeeper with carry-over hierarchy.
[GitHub]({GITHUB_URL}) · [Space]({HF_SPACE_URL})
            """
        )

        clock_state = gr.State(_new_clock())
        realtime_running = gr.State(False)

        with gr.Row():
            with gr.Column(scale=1, min_width=320):
                gr.Markdown("### Controls")
                ticks = gr.Slider(
                    minimum=0,
                    maximum=500000,
                    value=5000,
                    step=1000,
                    label="Advance ticks (batch)",
                )
                with gr.Row():
                    advance_btn = gr.Button("Advance", variant="primary")
                    reset_btn = gr.Button("Reset")
                preset = gr.Radio(
                    choices=[str(v) for v in PRESET_TICKS],
                    value="5000",
                    label="Presets",
                )
                gr.Markdown("### Real-time mode")
                rev_seconds = gr.Slider(
                    minimum=3600,
                    maximum=200000,
                    value=EARTH_DAY_SECONDS,
                    step=3600,
                    label="Gear 1 revolution (seconds)",
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
            with gr.Column(scale=2):
                clock_image = gr.Image(
                    label="Egg of Life clock face",
                    elem_id="clock-face",
                    interactive=False,
                )
                state_text = gr.Textbox(label="Gear state", lines=9, max_lines=12)

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