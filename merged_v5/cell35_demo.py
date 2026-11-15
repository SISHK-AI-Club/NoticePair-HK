import gradio as gr

demo = gr.Interface(
    fn=check_notice,
    inputs=[gr.Textbox(label="Traditional Chinese version", lines=8, value=fixture_zh),
            gr.Textbox(label="English version", lines=8, value=fixtures["2. Swapped dates (expect a deadline warning)"])],
    outputs=gr.Dataframe(label="Findings", wrap=True),
    title="Public Notice Check",
    description="A last check before a bilingual notice goes out. It flags sentences to review; a person makes the final call.",
)

RUN_DEMO = False
if RUN_DEMO:
    demo.launch(share=False, prevent_thread_lock=True)
else:
    print("Demo is optional. The regression benchmark runs in section 11.")