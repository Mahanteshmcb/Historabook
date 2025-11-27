from app import schemas
from app.utils.llm import generate_narration

def generate_plan(scene_title: str, characters: list, content_summary: str) -> schemas.LessonPlan:
    """
    V3 Planner: Generates a 3-part lesson (Intro, Deep Dive, Review).
    """
    segments = []
    
    # We will ask the AI to generate 3 distinct parts
    # This makes the "Next" button in the player actually useful.
    
    parts = [
        ("Intro", "Hook the student and introduce the setting."),
        ("Deep Dive", "Explain the main action or conflict in detail."),
        ("Review", "Summarize and ask a checking question.")
    ]
    
    print(f"🤖 Planning 3-part lesson for: {scene_title}...")

    for i, (part_name, instruction) in enumerate(parts):
        # Create a specific prompt for this part
        # We append the specific instruction to the summary
        context = f"{content_summary}\n\n(Focus on: {instruction})"
        
        # Ask AI
        ai_output = generate_narration(context, characters)
        
        # Build Segment
        segments.append(schemas.NarrationSegment(
            index=i,
            text=ai_output["narration"],
            visual=schemas.VisualSpec(
                character_focus=characters[0] if characters else None,
                background=ai_output["visual"],
                camera_action="zoom_in" if i == 0 else "pan_right",
                style="cinematic"
            ),
            analogy=f"Part {i+1} of 3",
            checkpoint_question=ai_output["quiz"] if i == 2 else None
        ))
    
    return schemas.LessonPlan(
        scene_id="temp_id",
        segments=segments
    )