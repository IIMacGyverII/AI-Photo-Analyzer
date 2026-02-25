# Quick Start Examples

## Getting Started

### 1. First-Time Setup

After installing the application, you'll need Ollama running with a vision model:

```bash
# Start Ollama (if not already running)
ollama serve

# Pull a vision model (in a new terminal)
ollama pull llava

# Verify it's working
ollama list
```

### 2. Launch the Application

```bash
# GUI mode (default)
python -m ollama_image_analyzer

# Or if installed as a package
ollama-image-analyzer
```

---

## GUI Examples

### Example 1: Analyze a Vacation Photo

1. **Launch the GUI**
2. **Drag and drop** your vacation photo into the left panel
3. The default prompt will analyze it comprehensively
4. Click **"Analyze Image"**
5. Wait for the analysis (progress bar shows activity)
6. Review the detailed description in the Response Preview
7. Find the saved analysis as `vacation_photo.txt` next to your image

### Example 2: Generate Product Descriptions

1. **Load a product image** (Import or drag-and-drop)
2. In **Prompt Enhancer**, click **"Load"**
3. Navigate to `prompts/` and select **`product_description.txt`**
4. Click **"Analyze Image"**
5. Get a structured product analysis with marketing copy!

### Example 3: Using a Remote Ollama Server

If your Ollama server is running on another machine:

1. Click **File → Settings** (or `Ctrl+,`)
2. Change **Host URL** to: `http://192.168.1.100:11434` (your server's IP)
3. Click **"Test Connection"** to verify
4. Click **🔄 Refresh** next to Model to load available models
5. Select your model and click **OK**
6. Now analyze images using the remote server!

---

## CLI Examples

### Example 1: Single Image Analysis

```bash
ollama-image-analyzer analyze photo.jpg
```

**Output:**
```
Connecting to Ollama at http://localhost:11434...
✓ Connected to Ollama
Using model: llava
Processing 1 image(s)

Analyzing images... ━━━━━━━━━━━━━━━━━━━━━━━━ 100%

┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Image       ┃ Status      ┃ Output           ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ photo.jpg   │ ✓ Success   │ photo.txt        │
└─────────────┴─────────────┴──────────────────┘

╭─ Summary ─────────────────────────────────╮
│ ✓ 1 succeeded                             │
╰───────────────────────────────────────────╯
```

### Example 2: Batch Processing

```bash
# Process all JPGs in the current directory
ollama-image-analyzer analyze *.jpg

# Or specific files
ollama-image-analyzer analyze photo1.jpg photo2.png photo3.webp
```

### Example 3: E-Commerce Product Batch

```bash
# Analyze all product images with product prompt
ollama-image-analyzer analyze products/*.jpg \
  --prompt prompts/product_description.txt \
  --output-dir ./product_descriptions

# Results will be in ./product_descriptions/
# - product1.txt
# - product2.txt
# - etc.
```

### Example 4: Remote Server with Custom Model

```bash
# Use a specific model on a remote server
ollama-image-analyzer analyze image.png \
  --host http://192.168.1.100:11434 \
  --model moondream

# Or set these as defaults and just run:
ollama-image-analyzer analyze image.png
```

### Example 5: Generate Alt Text for Website

```bash
# Create accessibility descriptions for all images
ollama-image-analyzer analyze website-images/*.jpg \
  --prompt prompts/accessibility_alt_text.txt \
  --output-dir ./alt-texts \
  --quiet

# Then use the results in your HTML:
# <img src="hero.jpg" alt="[content of hero.txt]">
```

### Example 6: Photography Analysis

```bash
# Analyze your photos technically
ollama-image-analyzer analyze my-photos/*.jpg \
  --prompt prompts/technical_photo_analysis.txt \
  --model llava \
  --verbose

# Great for learning from your shots!
```

---

## Custom Prompt Examples

### Create a Simple Custom Prompt

Create `prompts/social_media.txt`:

```
Analyze this image and create:

1. A catchy Instagram caption (max 150 characters)
2. 10 relevant hashtags
3. Best time to post (based on image content)
4. Target audience suggestion
```

Use it:
```bash
ollama-image-analyzer analyze post.jpg --prompt prompts/social_media.txt
```

### Create a Technical OCR Prompt

Create `prompts/receipt_parser.txt`:

```
Extract all information from this receipt/invoice:

- Store name
- Date and time
- All items with prices
- Subtotal, tax, total
- Payment method

Output in JSON format.
```

---

## Workflow Examples

### Workflow 1: Photo Cataloging

```bash
# Analyze entire photo collection
for dir in vacation-2024 wedding-photos family-reunion; do
  ollama-image-analyzer analyze "$dir"/*.jpg \
    --output-dir "$dir/descriptions" \
    --quiet
done

# Now you have searchable text descriptions for all photos!
```

### Workflow 2: Web Content Audit

```bash
# Extract all text from website screenshots
ollama-image-analyzer analyze screenshots/*.png \
  --prompt prompts/text_extraction.txt \
  --output-dir audit-results
```

### Workflow 3: Product Listing Automation

```bash
# Generate product descriptions
ollama-image-analyzer analyze products/*.jpg \
  --prompt prompts/product_description.txt \
  --output-dir listings

# Then process the .txt files to populate your store
```

---

## Tips & Tricks

### Tip 1: Speed Up Batch Processing

Use a faster model for bulk work:
```bash
ollama-image-analyzer analyze *.jpg --model moondream
```

### Tip 2: Preview Results

Use verbose mode to see what's happening:
```bash
ollama-image-analyzer analyze image.jpg --verbose
```

### Tip 3: Organize Results

Always use `--output-dir` for batch processing:
```bash
ollama-image-analyzer analyze *.jpg --output-dir ./analyzed
```

### Tip 4: Test Prompts Quickly

Use the GUI to refine your prompt on one image, then save it and use in CLI for batch processing!

### Tip 5: Chain Analysis

```bash
# First pass: general description
ollama-image-analyzer analyze *.jpg

# Second pass: extract text from those with text
ollama-image-analyzer analyze document-photos/*.jpg \
  --prompt prompts/text_extraction.txt \
  --output-dir extracted-text
```

---

## Troubleshooting

### Problem: "Connection failed"

```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve

# Test the connection
ollama-image-analyzer models
```

### Problem: "No vision models found"

```bash
# Install llava
ollama pull llava

# Verify
ollama list

# Refresh in GUI or try CLI
ollama-image-analyzer models
```

### Problem: Analysis is too slow

- Use a smaller/faster model (moondream is quick)
- Reduce image size before analysis
- Check server CPU/GPU usage
- Increase timeout if needed

---

## Advanced: Python API Usage

You can also use the components directly in Python:

```python
from pathlib import Path
from ollama_image_analyzer.core import OllamaAnalyzer, PromptManager

# Initialize
analyzer = OllamaAnalyzer(host="http://localhost:11434", model="llava")
prompts = PromptManager()

# Load a prompt
prompt = prompts.load_prompt(Path("prompts/default.txt"))

# Analyze
result = analyzer.analyze_image(Path("photo.jpg"), prompt)

if result.success:
    print(result.response)
    # Save
    analyzer.save_result(result)
else:
    print(f"Error: {result.error}")
```

---

**For more examples, check the [README.md](README.md) and explore the `prompts/` directory!**
