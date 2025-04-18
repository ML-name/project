import gradio as gr

def update_zoom(zoom_level, content):
    style = f"<div style='font-size:{zoom_level}px; white-space: pre-wrap;'>{content}</div>"
    return style

def clear_all():
    return (
        None,    # rubric
        None,    # submissions
        "",      # feedback_editor
        "",      # doc_raw_text
        "",      # doc_display (HTML)
        None,    # upload_past
        "",      # edit_prompt
        gr.update(value="Student 1"),  # reset dropdown
        gr.update(value="GPT"),        # reset model
        16       # reset zoom
    )

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):  # LEFT SIDE CONTROLS
            with gr.Row():
                gr.Markdown("## Upload to Create Feedback")
                gr.Button("+")
                gr.Button("-")

            rubric = gr.File(label="Requirement: Rubric")
            submissions = gr.File(file_types=[".docx"], file_count="multiple", label="Student Submission(s)")
            generate_btn = gr.Button("Generate Feedback")

            gr.Markdown("### Review / Edit / Download")
            student_selector = gr.Dropdown(choices=["Student 1", "Student 2", "Student 3"], label="Select Student")
            feedback_editor = gr.Textbox(lines=8, label="Edit Feedback")
            save_feedback = gr.Button("Save Feedback")

            with gr.Row():
                download_current = gr.Button("Download Current")
                download_all = gr.Button("Download All")

            gr.Markdown("### Model Settings")
            upload_past = gr.File(file_types=[".docx"], file_count="multiple", label="Upload Previous Assignments")
            model_choice = gr.Dropdown(choices=["GPT", "Gemini"], label="Model Choice")
            edit_prompt = gr.Textbox(lines=2, label="Edit Prompt")
            clear_history = gr.Button("Clear Model History")

        with gr.Column(scale=1):  # RIGHT SIDE VIEWER
            gr.Markdown("### Document Viewer / Editor")

            zoom_slider = gr.Slider(minimum=10, maximum=30, value=16, label="Zoom")
            doc_raw_text = gr.Textbox(visible=False) 
            doc_display = gr.HTML(label="Document Content")

            zoom_slider.change(fn=update_zoom, inputs=[zoom_slider, doc_raw_text], outputs=doc_display)

    # 🧹 CLEAR ALL BUTTON (Full Reset)
    clear_all_btn = gr.Button("🧹 Clear All Data (Reset App)")
    clear_all_btn.click(
        fn=clear_all,
        outputs=[
            rubric, submissions,
            feedback_editor,
            doc_raw_text, doc_display,
            upload_past, edit_prompt,
            student_selector, model_choice,
            zoom_slider
        ]
    )

demo.launch()