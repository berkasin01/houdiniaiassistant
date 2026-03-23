## GEN AI Wrangle – Help

### Overview
This tool uses an LLM (Gemini) to generate or fix VEX/Python code for Houdini, and to answer technical questions.

**[Youtube Tool Demo](https://youtu.be/wdFy118rs_o?si=bKMXtTbO47q_bFqc)**

---

### Run Over
Controls what the VEX wrangle runs over (**Detail, Primitives, Points, Vertices**).  
This is used both in the prompt and on the created Attribute Wrangle node.

---

### Mode

#### Message Mode
Ask general Houdini / VEX / Python questions. The model replies with an explanation (and small code examples if useful).

#### Create Code (VEX)
Generates a VEX snippet for an Attribute Wrangle based on your prompt and the selected **Run Over / Attributes / Node Path**.

#### Create Code (Python)
Generates Python using the `hou` module to work inside Houdini.

#### Code Fix (VEX)
Paste existing VEX into the **Code** box, describe what you want to change in the **Prompt**, and it will return an updated VEX snippet.

#### Code Fix (Python)
Same as above, but for Houdini Python code.

---

### Attributes
- **Find Attributes** inspects the selected SOP node and lists its attributes (with type and size). This context is passed to the LLM.
- **Disable Attributes** ignores this list and tells the model that no attribute information is provided.

---

### Node Path
- **Find Node** lets you pick a SOP node. Its path and attributes are sent as context.
- When you create a node from the result, the new wrangle / python node will be created in the same network, and will connect its input to the chosen node if possible.

---

### Prompt
- Describe what you want: behaviour, effect, or question.
- In Fix modes, this should describe how you want the pasted code to be changed or what is currently broken.

---

### Code (Fix modes only)
- Visible only in **Code Fix (VEX)** and **Code Fix (Python)**.
- Paste the existing code here; the model receives both the code and your Prompt and returns an updated version.

---

### Bottom Bar
- **Generate:** send the prompt to the model.
- **Code Commentary:** when enabled, the model is allowed to add brief comments explaining the code. When disabled, it is asked to output code only.
- **Clear:** reset the UI back to defaults.
- **?:** open this help window.

---

### Result Window
- Shows the raw LLM output.
- **Copy Code** copies just the code block between `<<<VEX>>>` / `<<<PYTHON>>>` and `<<<END>>>`.
- **Create Node** creates an Attribute Wrangle or Python node from the code (depending on the current Mode).
- **OK** closes the result window.
