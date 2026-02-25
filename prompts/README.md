# Prompt Templates

This folder contains prompt templates for the Ollama Image Analyzer.

## Available Presets

### 1. default.txt
Comprehensive image analysis with structured sections covering overview, visual elements, details, and interpretation.

### 2. product_description.txt
E-commerce focused analysis providing product identification, physical description, quality indicators, and marketing copy.

### 3. accessibility_alt_text.txt
Screen-reader friendly descriptions with 125 character limit, focusing on essential content in natural language.

### 4. technical_photo_analysis.txt
Photography-focused analysis including estimated camera settings, lighting, composition techniques, and improvement suggestions.

### 5. text_extraction.txt
OCR and text analysis extracting all visible text with location, context, and language detection.

### 6. ai_toolkit.txt
**NEW!** Specialized prompt for generating training captions for diffusion models (Flux.1-dev LoRAs via ai-toolkit):
- Natural language paragraphs (150-400 words)
- No markdown, bullets, headers, or JSON
- Extremely detailed scene descriptions
- **Trigger word support** in GUI (dynamically replaces `[trigger]` placeholder)
- Options for character vs. style training
- Perfect for AI model fine-tuning datasets

## Usage

### In GUI Mode

**Quick Selection:**
1. Use the **Preset** dropdown in the Prompt Enhancer section
2. Select any template from the list
3. **For AI-Toolkit**: A \"Trigger Word\" input will appear below
   - Leave blank for generic captions
   - Enter your trigger word (e.g., \"FLXDGT\", \"mychar\") to include it in descriptions

**Custom Prompts:**
1. Click \"📂 Load File\" to import any .txt file
2. Edit the prompt directly in the text area
3. Click \"💾 Save as Preset\" to save as a new template
4. Click \"🔄 Reset\" to restore the default prompt

### In CLI Mode
```bash
# Use default prompt
ollama-image-analyzer analyze image.jpg

# Use custom prompt
ollama-image-analyzer analyze image.jpg --prompt prompts/custom.txt
```

## Creating Custom Prompts

Simply create a new `.txt` file in this folder with your desired prompt text. The prompt will be sent to the Ollama vision model along with the image.

**In GUI:** After creating your custom prompt, it will automatically appear in the Preset dropdown after clicking the refresh button (🔄).

**In CLI:** Use the `--prompt` flag to specify your custom prompt file.

### Tips for Effective Prompts

1. **Be specific** about what you want to extract from images
2. **Structure your output** using markdown formatting for consistency (unless requesting plain text like AI-Toolkit)
3. **Include examples** of the desired output format if needed
4. **Set the context** (e.g., "You are an expert photographer analyzing composition")
5. **Use placeholders** like `[trigger]` for dynamic text replacement (see AI-Toolkit example)

### Special Feature: Trigger Word Replacement

For AI model training captions, you may want to insert a specific trigger word. The AI-Toolkit preset demonstrates this:

1. Include `[trigger]` in your prompt where the trigger word should appear
2. In **GUI mode**: When you select a preset with trigger word instructions, a "Trigger Word" input appears
3. Enter your trigger word, and the app automatically replaces `[trigger]` throughout the prompt
4. Perfect for creating consistent training datasets with custom identifiers

### Example Custom Prompts

**Product description prompt:**
```
Analyze this product image and provide:
- Product name and type
- Key features visible
- Condition assessment
- Suggested price range
- Marketing description (50 words)
```

**Accessibility prompt:**
```
Create an accessible alt text description for this image suitable for screen readers.
Be concise but informative. Limit to 125 characters.
```

**Technical photo analysis:**
```
Analyze this photograph's technical aspects:
- Estimated focal length and aperture
- Lighting setup
- Post-processing observations
- Composition rule application
- Suggestions for improvement
```
