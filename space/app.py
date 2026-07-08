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
# Named demo scenes — each loads a fresh clock at the given tick count
DEMO_SCENES: dict[str, tuple[int, str]] = {
    "Start": (0, "All seven gears at k=1 — the origin."),
    "PoC · 5k": (5000, "G1≈29% filled, G2=15 — classic proof-of-concept."),
    "Carry · 50k": (50000, "Carry propagates — watch G3+ advance."),
    "Deep · 500k": (500000, "Deep hierarchy — stress-test all seven gears."),
}
DEFAULT_DEMO = "PoC · 5k"

PANEL_HEIGHT = 860
CLOCK_VIEWPORT_SPAN = 2.12
CONTROLS_WIDTH = 220


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
    show_hands: bool,
    show_labels: bool,
    show_ticks: bool,
) -> tuple:
    image = render_clock_array(
        clock,
        figsize=(11, 11),
        dpi=110,
        show_ticks=show_ticks,
        show_labels=show_labels,
        show_hands=show_hands,
        slice_lines=slice_lines,
        title="",
        viewport_span=CLOCK_VIEWPORT_SPAN,
        tight_margins=True,
    )
    return image, _format_state(clock)


def _display_kwargs(
    slice_lines: int,
    overlays: list[str],
) -> dict:
    return {
        "slice_lines": slice_lines,
        "show_hands": "hands" in overlays,
        "show_labels": "labels" in overlays,
        "show_ticks": "ticks" in overlays,
    }


def _new_clock() -> UniversalPiClock:
    return UniversalPiClock()


def load_demo_scene(
    scene: str,
    slice_lines: int,
    overlays: list[str],
) -> tuple:
    """Load a named demo from scratch."""
    clock = _new_clock()
    ticks, _ = DEMO_SCENES.get(scene, (0, ""))
    if ticks:
        clock.fast_forward(ticks)
    return clock, *_render(clock, **_display_kwargs(slice_lines, overlays))


def demo_hint(scene: str) -> str:
    return DEMO_SCENES.get(scene, (0, ""))[1]


def step_clock(
    clock: UniversalPiClock | None,
    step: int,
    slice_lines: int,
    overlays: list[str],
) -> tuple:
    if clock is None:
        clock = _new_clock()
    if step > 0:
        clock.tick(step)
    return clock, *_render(clock, **_display_kwargs(slice_lines, overlays))


def reset_clock(
    slice_lines: int,
    overlays: list[str],
) -> tuple:
    clock = _new_clock()
    return clock, *_render(clock, **_display_kwargs(slice_lines, overlays))


def enable_realtime(
    clock: UniversalPiClock | None,
    rev_seconds: float,
    speed: float,
    slice_lines: int,
    overlays: list[str],
) -> tuple:
    if clock is None:
        clock = _new_clock()
    clock.set_earth_rate(rev_seconds)
    return (
        clock,
        True,
        speed,
        *_render(clock, **_display_kwargs(slice_lines, overlays)),
    )


def disable_realtime(
    clock: UniversalPiClock | None,
    slice_lines: int,
    overlays: list[str],
) -> tuple:
    if clock is None:
        clock = _new_clock()
    return (
        clock,
        False,
        1.0,
        *_render(clock, **_display_kwargs(slice_lines, overlays)),
    )


def realtime_tick(
    clock: UniversalPiClock | None,
    running: bool,
    speed: float,
    slice_lines: int,
    overlays: list[str],
) -> tuple:
    if clock is None:
        clock = _new_clock()
    if running and clock.tick_interval is not None:
        clock.tick_realtime(speed_multiplier=max(speed, 0.001))
    return clock, *_render(clock, **_display_kwargs(slice_lines, overlays))


def refresh_view(
    clock: UniversalPiClock | None,
    slice_lines: int,
    overlays: list[str],
) -> tuple:
    if clock is None:
        clock = _new_clock()
    return clock, *_render(clock, **_display_kwargs(slice_lines, overlays))


THEME = gr.themes.Base(
    primary_hue="orange",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill_dark="#0d1117",
    block_background_fill_dark="#161b22",
    block_border_width="1px",
    block_title_text_weight="600",
    block_padding="4px",
    layout_gap="6px",
)

CUSTOM_CSS = f"""
:root {{
    --panel-h: clamp(560px, calc(100vh - 7.5rem), {PANEL_HEIGHT}px);
    --controls-w: {CONTROLS_WIDTH}px;
}}
html, body, #root, .gradio-container {{
    height: 100% !important;
    max-height: 100vh !important;
    overflow: hidden !important;
}}
.gradio-container {{
    max-width: 100% !important;
    width: 100% !important;
    padding: 0.35rem 0.75rem 0.25rem !important;
}}
.gradio-container > .main,
.gradio-container > .main > .wrap {{
    height: 100% !important;
    max-height: 100vh !important;
    overflow: hidden !important;
}}
footer, .footer {{
    display: none !important;
}}
#app-header {{
    flex-shrink: 0;
    margin-bottom: 0 !important;
}}
#app-header h1 {{
    font-size: 1.15rem !important;
    margin: 0 !important;
    line-height: 1.25 !important;
}}
#app-header p {{
    font-size: 0.78rem !important;
    margin: 0.1rem 0 0 !important;
    opacity: 0.85;
}}
#main-row {{
    height: var(--panel-h) !important;
    max-height: var(--panel-h) !important;
    min-height: var(--panel-h) !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    overflow: hidden !important;
    gap: 0.65rem !important;
}}
#col-controls, #col-clock, #col-state {{
    height: var(--panel-h) !important;
    max-height: var(--panel-h) !important;
    overflow: hidden !important;
}}
#col-controls {{
    display: flex !important;
    flex-direction: column !important;
    max-width: var(--controls-w) !important;
    flex: 0 0 var(--controls-w) !important;
    padding-right: 0 !important;
}}
#controls-scroll {{
    height: var(--panel-h) !important;
    max-height: var(--panel-h) !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    padding-right: 0.25rem !important;
    scrollbar-width: thin;
    scrollbar-color: #3d4f5f #161b22;
}}
#controls-scroll .block {{
    margin-bottom: 0.2rem !important;
    padding: 4px 6px !important;
}}
#controls-scroll label,
#controls-scroll span,
#controls-scroll p {{
    font-size: 0.75rem !important;
}}
#controls-scroll input[type="number"] {{
    font-size: 0.75rem !important;
    padding: 1px 3px !important;
}}
#controls-scroll .gr-button {{
    font-size: 0.72rem !important;
    padding: 3px 6px !important;
    min-height: 1.6rem !important;
}}
#controls-scroll .section-header {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    margin: 0.15rem 0 !important;
}}
#demo-hint {{
    font-size: 0.68rem !important;
    line-height: 1.3 !important;
    opacity: 0.8;
    margin: 0 !important;
    padding: 2px 0 !important;
}}
#controls-scroll .accordion {{
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}}
#controls-scroll .accordion .label-wrap {{
    font-size: 0.72rem !important;
    padding: 4px 6px !important;
    min-height: unset !important;
}}
#col-clock {{
    flex: 1 1 auto !important;
    min-width: 0 !important;
    background: #0d1117 !important;
}}
#clock-viewport,
#clock-viewport > .form,
#clock-viewport > .block {{
    height: var(--panel-h) !important;
    max-height: var(--panel-h) !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    background: #0d1117 !important;
}}
#clock-face {{
    height: var(--panel-h) !important;
    max-height: var(--panel-h) !important;
    margin: 0 !important;
}}
#clock-face .image-container,
#clock-face .image-frame,
#clock-face [data-testid="image"] {{
    height: var(--panel-h) !important;
    max-height: var(--panel-h) !important;
    min-height: var(--panel-h) !important;
    width: 100% !important;
    background: #0d1117 !important;
    padding: 0 !important;
}}
#clock-face img {{
    width: 100% !important;
    height: 100% !important;
    max-height: var(--panel-h) !important;
    object-fit: contain !important;
    object-position: center center !important;
}}
#col-state {{
    display: flex !important;
    flex-direction: column !important;
    max-width: 340px !important;
    flex: 0 0 340px !important;
}}
#gear-state {{
    height: var(--panel-h) !important;
    max-height: var(--panel-h) !important;
    margin-top: 0 !important;
}}
#gear-state textarea {{
    height: calc(var(--panel-h) - 2.5rem) !important;
    max-height: calc(var(--panel-h) - 2.5rem) !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.35 !important;
    overflow-y: auto !important;
}}
@media (min-width: 1600px) and (min-height: 900px) {{
    :root {{
        --panel-h: {PANEL_HEIGHT}px;
    }}
}}
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

        with gr.Row(elem_id="main-row", equal_height=True, height=PANEL_HEIGHT):
            with gr.Column(scale=1, min_width=CONTROLS_WIDTH, elem_id="col-controls"):
                with gr.Column(elem_id="controls-scroll", variant="compact"):
                    gr.Markdown("**1 · Demo**", elem_classes=["section-header"])
                    demo_scene = gr.Dropdown(
                        choices=list(DEMO_SCENES.keys()),
                        value=DEFAULT_DEMO,
                        label="Scene",
                        show_label=False,
                    )
                    demo_hint_box = gr.Markdown(
                        demo_hint(DEFAULT_DEMO),
                        elem_id="demo-hint",
                    )
                    reload_demo_btn = gr.Button("Load scene", variant="primary", size="sm")

                    gr.Markdown("**2 · View**", elem_classes=["section-header"])
                    slice_lines = gr.Dropdown(
                        choices=SLICE_LINE_CHOICES,
                        value=DEFAULT_SLICE_LINES,
                        label="Slice lines",
                    )
                    overlays = gr.CheckboxGroup(
                        choices=[
                            ("Hands", "hands"),
                            ("k/π labels", "labels"),
                            ("Slice ticks", "ticks"),
                        ],
                        value=["hands", "labels", "ticks"],
                        label="Overlays",
                    )

                    with gr.Accordion("3 · Manual step", open=False):
                        step_ticks = gr.Number(
                            value=1000,
                            precision=0,
                            label="Ticks per step",
                            minimum=1,
                            maximum=500000,
                        )
                        with gr.Row():
                            step_btn = gr.Button("+ Step", size="sm")
                            reset_btn = gr.Button("Reset", size="sm")

                    with gr.Accordion("4 · Live Earth rate", open=False):
                        rev_seconds = gr.Slider(
                            minimum=3600,
                            maximum=200000,
                            value=EARTH_DAY_SECONDS,
                            step=3600,
                            label="Gear 1 day (s)",
                        )
                        speed = gr.Slider(
                            minimum=1,
                            maximum=10000,
                            value=1000,
                            step=10,
                            label="Speed ×",
                        )
                        with gr.Row():
                            start_rt = gr.Button("▶ Start", size="sm")
                            stop_rt = gr.Button("■ Stop", size="sm")

            with gr.Column(scale=11, min_width=640, elem_id="col-clock"):
                with gr.Column(elem_id="clock-viewport"):
                    clock_image = gr.Image(
                        elem_id="clock-face",
                        interactive=False,
                        show_label=False,
                        height=PANEL_HEIGHT,
                        buttons=[],
                    )

            with gr.Column(scale=3, min_width=280, elem_id="col-state"):
                state_text = gr.Textbox(
                    label="Gear state",
                    elem_id="gear-state",
                    lines=14,
                    max_lines=14,
                    interactive=False,
                )

        timer = gr.Timer(0.15, active=False)

        display_inputs = [slice_lines, overlays]
        outputs = [clock_state, clock_image, state_text]
        rt_outputs = [clock_state, realtime_running, speed, clock_image, state_text]
        view_outputs = [clock_state, clock_image, state_text]

        reload_demo_btn.click(
            load_demo_scene,
            inputs=[demo_scene, *display_inputs],
            outputs=outputs,
        ).then(lambda: False, outputs=realtime_running).then(
            lambda: gr.Timer(active=False),
            outputs=timer,
        )

        demo_scene.change(
            demo_hint,
            inputs=demo_scene,
            outputs=demo_hint_box,
        ).then(
            load_demo_scene,
            inputs=[demo_scene, *display_inputs],
            outputs=outputs,
        ).then(lambda: False, outputs=realtime_running).then(
            lambda: gr.Timer(active=False),
            outputs=timer,
        )

        reset_btn.click(
            reset_clock,
            inputs=display_inputs,
            outputs=outputs,
        ).then(lambda: False, outputs=realtime_running).then(
            lambda: gr.Timer(active=False),
            outputs=timer,
        )

        step_btn.click(
            step_clock,
            inputs=[clock_state, step_ticks, *display_inputs],
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

        for control in (slice_lines, overlays):
            control.change(
                refresh_view,
                inputs=[clock_state, *display_inputs],
                outputs=view_outputs,
            )

        timer.tick(
            realtime_tick,
            inputs=[clock_state, realtime_running, speed, *display_inputs],
            outputs=view_outputs,
            show_progress="hidden",
        )

        demo.load(
            load_demo_scene,
            inputs=[demo_scene, *display_inputs],
            outputs=outputs,
        )

    return demo


if __name__ == "__main__":
    build_demo().launch(theme=THEME, css=CUSTOM_CSS)