import os
from PySide6.QtWidgets import (
    QMainWindow, QStyle, QToolButton, QPushButton, QWidget, QVBoxLayout,
    QLineEdit, QHBoxLayout, QLabel, QFileDialog, QComboBox, QApplication,
    QCheckBox, QTextEdit, QDialog, QPlainTextEdit, QSizePolicy  # <-- add this
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

import hou
from google import genai

API_KEY = "PASTE YOUR API KEY HERE"
HOUDINI_VERSION = hou.applicationVersionString()


class appUI(QMainWindow):
    def __init__(self, parent=None):
        super(appUI, self).__init__(parent)

        self.setWindowTitle("GEN AI Wrangle")

        # --- main layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(6)

        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(6)

        row3 = QHBoxLayout()
        row3.setContentsMargins(0, 0, 0, 0)
        row3.setSpacing(6)

        row4 = QHBoxLayout()
        row4.setContentsMargins(0, 0, 0, 0)
        row4.setSpacing(6)

        row5 = QHBoxLayout()
        row5.setContentsMargins(0, 0, 0, 0)
        row5.setSpacing(6)

        row6 = QHBoxLayout()
        row6.setContentsMargins(0, 0, 0, 0)
        row6.setSpacing(6)

        # central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # ------------------------------------------------------------------ #
        # Row 1 – Run Over / Mode
        # ------------------------------------------------------------------ #
        self.label = QLabel("Run Over:")
        self.dropdown = QComboBox()
        self.dropdown.addItem("Detail(only once)")
        self.dropdown.addItem("Primitives")
        self.dropdown.addItem("Points")
        self.dropdown.addItem("Vertices")

        self.run_over_config = [
            {"scope": "detail", "class": 3},  # Detail(only once)
            {"scope": "prims", "class": 1},  # Primitives
            {"scope": "points", "class": 0},  # Points
            {"scope": "vertices", "class": 2},  # Vertices
        ]

        self.label_mode = QLabel("Mode:")
        self.dropdown_mode = QComboBox()
        self.dropdown_mode.addItem("Message Mode")
        self.dropdown_mode.addItem("Create Code(VEX)")
        self.dropdown_mode.addItem("Create Code(Python)")
        self.dropdown_mode.addItem("Code Fix(VEX)")
        self.dropdown_mode.addItem("Code Fix(Python)")

        # Make the two combo boxes share space nicely
        self.dropdown.setMinimumWidth(140)
        self.dropdown_mode.setMinimumWidth(160)

        default_option_index = 2
        cfg = self.run_over_config[default_option_index]
        self.run_over_scope = cfg["scope"]
        self.run_over_class = cfg["class"]

        row1.addWidget(self.label)
        row1.addWidget(self.dropdown, 1)
        row1.addSpacing(12)
        row1.addWidget(self.label_mode)
        row1.addWidget(self.dropdown_mode, 1)
        layout.addLayout(row1)

        # ------------------------------------------------------------------ #
        # Shared label width for rows 2–5
        # ------------------------------------------------------------------ #
        label_width = 70

        # ------------------------------------------------------------------ #
        # Row 2 – Attributes
        # ------------------------------------------------------------------ #
        self.attr_label = QLabel("Attributes:")
        self.attr_label.setFixedWidth(label_width)

        self.attrs_edit = QLineEdit()

        self.att_button = QPushButton("Find Attributes")
        self.att_button.clicked.connect(self.find_attributes)

        self.disable_att = QCheckBox("Disable Attributes")
        self.disable_att.setChecked(False)
        self.att_enable_toggle(self.disable_att.isChecked())
        self.disable_att.stateChanged.connect(self.att_enable_toggle)

        row2.addWidget(self.attr_label)
        row2.addWidget(self.attrs_edit, 1)
        row2.addWidget(self.att_button)
        row2.addWidget(self.disable_att)
        layout.addLayout(row2)

        # ------------------------------------------------------------------ #
        # Row 3 – Node Path
        # ------------------------------------------------------------------ #
        self.node_label = QLabel("Node Path:")
        self.node_label.setFixedWidth(label_width)

        self.node_path_box = QLineEdit()
        self.node_path_button = QPushButton("Find Node")
        self.node_path_button.clicked.connect(self.find_node_path)

        row3.addWidget(self.node_label)
        row3.addWidget(self.node_path_box, 1)
        row3.addWidget(self.node_path_button)
        layout.addLayout(row3)

        # Small gap before text areas
        layout.addSpacing(4)

        # ------------------------------------------------------------------ #
        # Row 4 – Prompt (multi-line)
        # ------------------------------------------------------------------ #
        self.label_text_box = QLabel("Prompt:")
        self.label_text_box.setFixedWidth(label_width)
        self.label_text_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.prompt_text_box = QTextEdit()
        self.prompt_text_box.setPlaceholderText("Type here...")
        self.prompt_text_box.setMinimumHeight(120)

        row4.addWidget(self.label_text_box)
        row4.addWidget(self.prompt_text_box, 1)
        layout.addLayout(row4)

        # ------------------------------------------------------------------ #
        # Row 5 – Code (Fix modes only)
        # ------------------------------------------------------------------ #
        self.code_prompt_box = QLabel("Code:")
        self.code_prompt_box.setFixedWidth(label_width)
        self.code_prompt_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.code_prompt_box.hide()

        self.code_prompt_text_box = QTextEdit()
        self.code_prompt_text_box.setPlaceholderText("Add Code to Fix here...")
        self.code_prompt_text_box.setMinimumHeight(100)
        self.code_prompt_text_box.hide()

        row5.addWidget(self.code_prompt_box)
        row5.addWidget(self.code_prompt_text_box, 1)
        layout.addLayout(row5)

        # Small gap before bottom bar
        layout.addSpacing(4)

        # ------------------------------------------------------------------ #
        # Row 6 – Status + buttons
        # ------------------------------------------------------------------ #
        self.gen_button = QPushButton("Generate")
        self.gen_button.clicked.connect(self.gen_button_func)
        # let Generate grow to fill the free space on the row
        self.gen_button.setMinimumWidth(110)
        self.gen_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.code_comm_togg = QCheckBox("Code Commentary")
        self.code_comm_togg.setChecked(False)
        self.code_with_comments = False
        self.code_comm_togg.toggled.connect(self.code_commentary_toggle)

        self.help_button = QToolButton()
        self.help_button.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_button.setAutoRaise(True)
        self.help_button.setToolTip("Show help")
        self.help_button.clicked.connect(self.show_help)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)

        self.status_label = QLabel("Ready")

        row6.addWidget(self.status_label)
        row6.addSpacing(10)  # small gap after status
        row6.addWidget(self.gen_button, 1)  # stretch factor -> takes leftover space
        row6.addWidget(self.code_comm_togg)
        row6.addWidget(self.clear_button)
        row6.addWidget(self.help_button)
        layout.addLayout(row6)

        # ------------------------------------------------------------------ #
        # Defaults / shortcuts
        # ------------------------------------------------------------------ #
        self.dropdown.currentIndexChanged.connect(self.dropdown_selection)
        self.dropdown_mode.currentIndexChanged.connect(self.dropdown_selection_mode)

        default_run_over_index = 2  # Points
        default_mode_index = 1  # Create Code(VEX)

        self.dropdown.setCurrentIndex(default_run_over_index)
        self.dropdown_mode.setCurrentIndex(default_mode_index)

        self.dropdown_selection(default_run_over_index)
        self.dropdown_selection_mode(default_mode_index)

        self.short_gen_return = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.short_gen_return.activated.connect(self.gen_button.click)

        self.short_gen_ctrl_enter = QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Return), self)
        self.short_gen_ctrl_enter.activated.connect(self.gen_button.click)

        self.short_clear = QShortcut(QKeySequence("Ctrl+R"), self)
        self.short_clear.activated.connect(self.clear_button.click)

        self.short_help = QShortcut(QKeySequence(Qt.Key_F1), self)
        self.short_help.activated.connect(self.help_button.click)

        self.resize(540, 260)

    def set_status(self, text):
        self.status_label.setText(text)
        QApplication.processEvents()

    def show_llm_result(self, text):
        dlg = QDialog(self)
        dlg.setWindowTitle("LLM Result")

        layout = QVBoxLayout(dlg)
        horizontal_layout = QHBoxLayout()
        horizontal_layout2 = QHBoxLayout()

        label = QLabel("")
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        ok_btn = QPushButton("OK")
        ok_btn.setEnabled(False)
        ok_btn.clicked.connect(dlg.accept)

        create_wrangle_btn = QPushButton("Create Node")
        create_wrangle_btn.setEnabled(False)

        copy_code_btn = QPushButton("Copy Code")
        copy_code_btn.setEnabled(False)

        # ---- extract code block from the full text ----
        raw_text = text or ""

        def extract_code_block(t):
            if not t:
                return ""
            # prefer Python, then VEX – adjust if you want the opposite
            if "<<<PYTHON>>>" in t:
                start_tag = "<<<PYTHON>>>"
            elif "<<<VEX>>>" in t:
                start_tag = "<<<VEX>>>"
            else:
                return ""

            end_tag = "<<<END>>>"
            start = t.find(start_tag)
            if start == -1:
                return ""
            start += len(start_tag)
            end = t.find(end_tag, start)
            if end == -1:
                end = len(t)
            return t[start:end].strip()

        code_block = extract_code_block(raw_text)

        def on_copy_code_clicked():
            if code_block:
                QApplication.clipboard().setText(code_block)

        copy_code_btn.clicked.connect(on_copy_code_clicked)

        def on_create_wrangle_clicked():
            self.create_wrangle_from_text(raw_text)

        create_wrangle_btn.clicked.connect(on_create_wrangle_clicked)

        horizontal_layout.addWidget(label)
        horizontal_layout2.addWidget(copy_code_btn)
        horizontal_layout2.addWidget(create_wrangle_btn)
        horizontal_layout2.addWidget(ok_btn)
        layout.addLayout(horizontal_layout)
        layout.addLayout(horizontal_layout2)

        if not raw_text:
            label.setText("")
            ok_btn.setEnabled(True)
            create_wrangle_btn.setEnabled(False)
            copy_code_btn.setEnabled(False)
        else:
            state = {"i": 0}
            timer = QTimer(dlg)

            def tick():
                i = state["i"]
                label.setText(raw_text[:i])
                state["i"] += 1
                if state["i"] > len(raw_text):
                    timer.stop()
                    ok_btn.setEnabled(True)
                    has_code = bool(code_block)
                    create_wrangle_btn.setEnabled(has_code)
                    copy_code_btn.setEnabled(has_code)

            timer.timeout.connect(tick)
            timer.start(20)

        dlg.resize(600, 300)
        dlg.setWindowModality(Qt.NonModal)
        dlg.show()

    def gen_button_func(self, index=None):
        mode_selected_index = self.selected_option_mode_index
        mode_selected_name = self.selected_option_mode_text

        prompt_text = self.prompt_text_box.toPlainText().strip()
        if not prompt_text:
            hou.ui.displayMessage("Prompt is empty.\nPlease describe what you want first.")
            self.set_status("Ready")
            return

        if mode_selected_index in (3, 4):
            code_text = self.code_prompt_text_box.toPlainText().strip()
            if not code_text:
                hou.ui.displayMessage("Code box is empty.\nPaste the code you want to fix.")
                self.set_status("Ready")
                return

        handlers = {
            0: self.message_mode,
            1: self.create_vex_code_mode,
            2: self.create_python_code_mode,
            3: self.fix_code_vex,
            4: self.fix_code_python,
        }

        handler = handlers.get(mode_selected_index)
        if not handler:
            self.set_status("Ready")
            return

        self.set_status("Calling Gemini…")

        answer = handler()

        if not answer:
            self.set_status("No response")
            return

        status = "Response received"

        if mode_selected_index in (1, 3):
            code_block = self._extract_code_block(answer, "<<<VEX>>>", "<<<END>>>")
            if code_block:
                n_lines = len([l for l in code_block.splitlines() if l.strip()])
                status = f"Response received (VEX, {n_lines} lines)"
        elif mode_selected_index in (2, 4):
            code_block = self._extract_code_block(answer, "<<<PYTHON>>>", "<<<END>>>")
            if code_block:
                n_lines = len([l for l in code_block.splitlines() if l.strip()])
                status = f"Response received (Python, {n_lines} lines)"
        else:
            status = "Response received (message)"

        self.set_status(status)
        self.show_llm_result(answer)

    def _extract_code_block(self, full_text, start_marker, end_marker):
        try:
            start_idx = full_text.index(start_marker) + len(start_marker)
            end_idx = full_text.index(end_marker, start_idx)
        except ValueError:
            return None
        code = full_text[start_idx:end_idx].strip()
        return code or None

    def create_wrangle_from_text(self, full_text):
        mode_index = getattr(self, "selected_option_mode_index", 0)

        if mode_index in (1, 3):
            code = self._extract_code_block(full_text, "<<<VEX>>>", "<<<END>>>")
            if not code:
                hou.ui.displayMessage(
                    "Could not find VEX code between <<<VEX>>> and <<<END>>>."
                )
                return
            self._create_vex_wrangle_node(code)

        elif mode_index in (2, 4):
            code = self._extract_code_block(full_text, "<<<PYTHON>>>", "<<<END>>>")
            if not code:
                hou.ui.displayMessage(
                    "Could not find Python code between <<<PYTHON>>> and <<<END>>>."
                )
                return
            self._create_python_node(code)

        else:
            hou.ui.displayMessage(
                "Current mode does not support creating a wrangle from the result."
            )

    def _create_vex_wrangle_node(self, code):
        node_path = self.node_path_box.text().strip()
        base_node = hou.node(node_path) if node_path else None

        # choose parent
        if base_node is not None:
            parent = base_node.parent()
        else:
            net = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            parent = net.pwd() if net is not None else hou.node("/obj")

        wrangle = parent.createNode("attribwrangle", "gen_ai_vex_wrangle")

        if base_node is not None:
            wrangle.setInput(0, base_node)

        run_over_class = getattr(self, "run_over_class", 0)
        remap_run_over = {0: 2,
                          1: 1,
                          2: 3,
                          3: 2, }

        wrangle.parm("class").set(remap_run_over[run_over_class])
        wrangle.parm("snippet").set(code)
        wrangle.moveToGoodPosition()

    def _create_python_node(self, code):
        # try to get base node from Node Path
        node_path = self.node_path_box.text().strip()
        base_node = hou.node(node_path) if node_path else None

        # choose parent
        if base_node is not None:
            parent = base_node.parent()
        else:
            net = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            parent = net.pwd() if net is not None else hou.node("/obj")

        py_node = parent.createNode("python", "gen_ai_python")

        # connect if we have a base node
        if base_node is not None:
            py_node.setInput(0, base_node)

        py_node.parm("python").set(code)
        py_node.moveToGoodPosition()

    def message_mode(self):
        user_prompt = self.prompt_text_box.toPlainText()

        node_path = self.node_path_box.text()
        if len(node_path) == 0:
            node_path = "Node Path not provided"

        disable_att_toggle = self.toggle_result
        if disable_att_toggle:
            attributes = "No attributes provided"
        else:
            attributes = self.attrs_edit.text()

        run_over_mode_text = self.selected_option_run_over

        commentary_toggle = self.code_with_comments
        if commentary_toggle:
            commentary = "Provide Commentary with the Code"
        else:
            commentary = "Do not add ANY Commentary to the Code"

        prompt = f"""
        You are an expert Houdini TD and technical mentor.

        Context:
        - Houdini version: {HOUDINI_VERSION}
        - Current tool: AI helper for workflows in Houdini.
        - Run Over mode currently selected in the UI: {run_over_mode_text}
        - Target node path (if any): {node_path}
        - Known attributes on the geometry of the target node:
        {attributes}

        Task:
        1. Read the user request below.
        2. If the user is mainly asking for explanation, guidance, or debugging help, answer in clear natural language.
        3. If the user explicitly asks for code (VEX or Python), or a short example would clearly help, provide a brief, production-ready code snippet **in addition to** the explanation.

        User request:
        {user_prompt}

        Constraints:
        - Give a concise, production-oriented answer focused on Houdini and its workflows.
        - Prefer step-by-step explanation when it helps, but keep it focused.
        - Only include code when the user asks for it or when a small example is clearly the simplest way to explain.
        - When you include code, clearly label the language (e.g. "VEX example:" or "Python example:") and keep the snippet short and directly usable.
        - Do not invent non-existent Houdini features or nodes; if you are unsure, say so.
        - Avoid generic motivational text and long disclaimers; focus on concrete, technical guidance.

        Output format:
        - Start your answer with a line containing exactly: <<<MESSAGE>>>
        - Then write your explanation and any optional short code examples.
        - End your answer with a line containing exactly: <<<END>>>
        - Between these markers, output only the answer text (no markdown backticks).
        """

        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    def create_vex_code_mode(self):
        user_prompt = self.prompt_text_box.toPlainText()

        node_path = self.node_path_box.text()
        if len(node_path) == 0:
            node_path = "Node Path not provided"

        disable_att_toggle = self.toggle_result
        if disable_att_toggle:
            attributes = "No attributes provided"
        else:
            attributes = self.attrs_edit.text()

        run_over_mode_text = self.selected_option_run_over

        commentary_toggle = self.code_with_comments
        if commentary_toggle:
            commentary = "Provide Commentary with the Code"
        else:
            commentary = "Do not add ANY Commentary to the Code"

        prompt = f"""
        You are an expert Houdini TD and VEX programmer.

        Context:
        - Houdini version: {HOUDINI_VERSION}
        - Target node: Attribute Wrangle SOP
        - Run Over: {run_over_mode_text} (VEX scope: {run_over_mode_text})
        - Geometry node path: {node_path}
        - Known attributes on the geometry: {attributes}

        Task:
        1. From the user's request below, identify the part that requires VEX code (geometry/attribute logic).
        2. Write VEX code for the Attribute Wrangle's "Snippet" parameter that implements ONLY that technical part.
        3. If the user also asks any general, conversational, or explanatory question (e.g. "tell me how your day is"), answer that in natural language AFTER the VEX block, not inside the code.

        User request:
        {user_prompt}

        Constraints for the VEX snippet:
        - VEX only, valid inside an Attribute Wrangle SOP.
        - Do NOT create or describe nodes, UIs, or parameters; only write the VEX snippet.
        - Use existing attributes when they are listed above. If you introduce new attributes, declare them explicitly with the correct type (e.g. f@foo, v@bar, i@id).
        - Do not use external files, Python, or HScript.
        - Do NOT include conversational messages, jokes, or descriptions of your day inside the VEX code.
        - Do NOT use printf or other I/O functions unless the user explicitly asks you to add logging or debug output.
        - {commentary}

        Output format:
        1. First, output ONLY the VEX snippet between these markers:
           <<<VEX>>>
           [VEX code here]
           <<<END>>>

        2. After the <<<END>>> line, if the user asked any non-code question (for example, asking about your day or requesting an explanation), answer it in plain natural language.
        3. Do not put any VEX code outside the <<<VEX>>> ... <<<END>>> block.
        """

        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        answer = response.text

        return answer

    def create_python_code_mode(self):
        user_prompt = self.prompt_text_box.toPlainText()

        node_path = self.node_path_box.text()
        if len(node_path) == 0:
            node_path = "Node Path not provided"

        disable_att_toggle = self.toggle_result
        if disable_att_toggle:
            attributes = "No attributes provided"
        else:
            attributes = self.attrs_edit.text()

        run_over_mode_text = self.selected_option_run_over

        commentary_toggle = self.code_with_comments
        if commentary_toggle:
            commentary = "Provide Commentary with the Code"
        else:
            commentary = "Do not add ANY Commentary to the Code"

        prompt = f"""
        You are an expert Houdini TD and Python developer.

        Context:
        - Houdini version: {HOUDINI_VERSION}
        - Execution environment: Python code run inside Houdini (Python Shell, shelf tool, or parameter callback).
        - Run Over mode currently selected in the UI: {run_over_mode_text}
        - Target node path (if any): {node_path}
        - Known attributes on the geometry of the target node: {attributes}

        Task:
        1. From the user's request below, identify the part that requires Python code to interact with Houdini.
        2. Write Python code that implements ONLY that technical part.
        3. If the user also asks any general, conversational, or explanatory question, answer that in natural language AFTER the Python block, not inside the code.

        User request:
        {user_prompt}

        Constraints for the Python code:
        - Python 3, using Houdini's 'hou' module when interacting with the scene.
        - Do NOT write VEX, HScript, or node graph descriptions; only Python code.
        - Do not import external third-party libraries; only the standard library and 'hou' may be used.
        - The code must be directly pasteable into the Python Shell or a shelf tool without additional explanation.
        - If the target node path is provided, treat it as the primary node to operate on.
        - Do NOT include conversational messages, jokes, or descriptions of your day inside the Python code.
        - Avoid print statements that are only for chatting with the user; only use print or logging if the user explicitly asks for debug output or console messages.
        - {commentary}

        Output format:
        1. First, output ONLY the Python code between these markers:
           <<<PYTHON>>>
           [Python code here]
           <<<END>>>

        2. After the <<<END>>> line, if the user asked any non-code question (for example, asking about your day or requesting an explanation), answer it in plain natural language.
        3. Do not put any Python code outside the <<<PYTHON>>> ... <<<END>>> block.
        """

        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        answer = response.text

        return answer

    def fix_code_vex(self):
        user_prompt = self.prompt_text_box.toPlainText()

        code_fix = self.code_prompt_text_box.toPlainText()

        node_path = self.node_path_box.text()
        if len(node_path) == 0:
            node_path = "Node Path not provided"

        disable_att_toggle = self.toggle_result
        if disable_att_toggle:
            attributes = "No attributes provided"
        else:
            attributes = self.attrs_edit.text()

        run_over_mode_text = self.selected_option_run_over

        commentary_toggle = self.code_with_comments
        if commentary_toggle:
            commentary = "Provide Commentary with the Code"
        else:
            commentary = "Do not add ANY Commentary to the Code"
        prompt = f"""
        You are an expert Houdini TD and VEX programmer.

        Context:
        - Houdini version: {HOUDINI_VERSION}
        - Target node: Attribute Wrangle SOP
        - Run Over: {run_over_mode_text} (VEX scope: {run_over_mode_text})
        - Geometry node path: {node_path}
        - Known attributes on the geometry: {attributes}

        Existing VEX code that needs to be fixed or improved:
        <<<ORIGINAL_VEX>>>
        {code_fix}
        <<<END_ORIGINAL_VEX>>>

        Task:
        1. Treat the code above as the starting point.
        2. Modify or fix it so that it satisfies this request from the user:
        {user_prompt}
        3. Preserve the overall intent and structure of the original code wherever it still makes sense; only change what is needed to fulfil the request.

        Constraints for the updated VEX snippet:
        - VEX only, valid inside an Attribute Wrangle SOP.
        - Do NOT create or describe nodes, UIs, or parameters; only write the VEX snippet.
        - Use existing attributes when they are listed above. If you introduce new attributes, declare them explicitly with the correct type (e.g. f@foo, v@bar, i@id).
        - Do not use external files, Python, or HScript.
        - Do NOT include conversational messages, jokes, or descriptions of your day inside the VEX code.
        - Do NOT use printf or other I/O functions unless the user explicitly asks you to add logging or debug output.
        - {commentary}

        Output format:
        1. First, output ONLY the updated VEX snippet between these markers:
           <<<VEX>>>
           [updated VEX code here]
           <<<END>>>

        2. After the <<<END>>> line, if the user also asked for explanation or clarification, you may briefly explain the main changes in natural language.
        3. Do not put any VEX code outside the <<<VEX>>> ... <<<END>>> block.
        """

        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        answer = response.text

        return answer

    def fix_code_python(self):
        user_prompt = self.prompt_text_box.toPlainText()
        code_fix = self.code_prompt_text_box.toPlainText()

        node_path = self.node_path_box.text()
        if len(node_path) == 0:
            node_path = "Node Path not provided"

        disable_att_toggle = self.toggle_result
        if disable_att_toggle:
            attributes = "No attributes provided"
        else:
            attributes = self.attrs_edit.text()

        run_over_mode_text = self.selected_option_run_over

        commentary_toggle = self.code_with_comments
        if commentary_toggle:
            commentary = "Include concise inline comments explaining the main changes."
        else:
            commentary = "Do not add ANY comments or explanations; output code only."

        prompt = f"""
            You are an expert Houdini TD and Python developer.

            Context:
            - Houdini version: {HOUDINI_VERSION}
            - Execution environment: Python code run inside Houdini (Python Shell, shelf tool, or parameter callback).
            - Run Over mode currently selected in the UI: {run_over_mode_text}
            - Target node path (if any): {node_path}
            - Known attributes on the geometry of the target node: {attributes}

            Existing Python code that needs to be fixed or improved:
            <<<ORIGINAL_PYTHON>>>
            {code_fix}
            <<<END_ORIGINAL_PYTHON>>>

            Task:
            1. Treat the code above as the starting point.
            2. Modify or fix it so that it satisfies this request from the user:
            {user_prompt}
            3. Preserve the overall intent and structure of the original code wherever it still makes sense; only change what is needed to fulfil the request.

            Constraints for the updated Python code:
            - Python 3, using Houdini's 'hou' module when interacting with the scene.
            - Do NOT write VEX, HScript, or node graph descriptions; only Python code.
            - Do not import external third-party libraries; only the standard library and 'hou' may be used.
            - The code must be directly pasteable into the Python Shell, a Python SOP, or a shelf tool without additional explanation.
            - If the target node path is provided, treat it as the primary node to operate on.
            - Do NOT include conversational messages, jokes, or descriptions of your day inside the Python code.
            - Avoid print statements that are only for chatting with the user; only use print or logging if the user explicitly asks for debug output or console messages.
            - {commentary}

            Output format:
            1. First, output ONLY the updated Python code between these markers:
               <<<PYTHON>>>
               [updated Python code here]
               <<<END>>>

            2. After the <<<END>>> line, if the user also asked for explanation or clarification, you may briefly explain the main changes in natural language.
            3. Do not put any Python code outside the <<<PYTHON>>> ... <<<END>>> block.
            """

        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        answer = response.text
        return answer

    def att_enable_toggle(self, state):
        if state == 2:
            self.toggle_result = True
            self.attrs_edit.setDisabled(True)
            self.att_button.setDisabled(True)
        else:
            self.toggle_result = False
            self.attrs_edit.setDisabled(False)
            self.att_button.setDisabled(False)

    def clear(self):
        # reset dropdowns
        self.dropdown.setCurrentIndex(2)
        self.dropdown_selection(2)

        self.dropdown_mode.setCurrentIndex(1)
        self.dropdown_selection_mode(1)

        # clear node path + attributes
        self.node_path_box.clear()
        self.attrs_edit.clear()

        # reset toggle
        self.disable_att.setChecked(False)

        self.code_prompt_text_box.clear()

        self.prompt_text_box.clear()
        self.code_prompt_text_box.hide()
        self.code_prompt_box.hide()

        self.code_comm_togg.setChecked(False)

        self.set_status("Ready")

    def dropdown_selection(self, index):
        self.selected_option_run_over = self.dropdown.itemText(index)
        cfg = self.run_over_config[index]
        self.run_over_index = index
        self.run_over_scope = cfg["scope"]
        self.run_over_class = cfg["class"]

    def dropdown_selection_mode(self, index):
        self.selected_option_mode_index = index
        self.selected_option_mode_text = self.dropdown_mode.itemText(index)

        # Show / hide the Code box depending on mode
        if index in (3, 4):  # Code Fix(VEX), Code Fix(Python)
            self.code_prompt_box.show()
            self.code_prompt_text_box.show()
        else:  # Message, Create VEX, Create Python
            self.code_prompt_box.hide()
            self.code_prompt_text_box.hide()

        # Enable/disable Code Commentary depending on mode
        if index == 0:  # Message Mode
            self.code_comm_togg.setChecked(False)
            self.code_comm_togg.setEnabled(False)
        else:
            self.code_comm_togg.setEnabled(True)

    def code_commentary_toggle(self, checked):
        self.code_with_comments = checked

    def get_attrs_block(self, path, scope="points"):
        node = hou.node(path)
        if node is None:
            raise hou.Error("Node not found: " + path)

        node.cook()
        geo = node.geometry()

        scope = scope.lower()
        if scope == "points":
            attribs = geo.pointAttribs()
        elif scope in ("prims", "primitives"):
            attribs = geo.primAttribs()
        elif scope == "vertices":
            attribs = geo.vertexAttribs()
        else:  # detail
            attribs = geo.globalAttribs()

        lines = []
        for a in attribs:
            dt = str(a.dataType()).split(".")[-1].lower()
            lines.append(f"@{a.name()} ({dt}[{a.size()}]),")

        return "\n".join(lines)

    def find_node_path(self):
        path = hou.ui.selectNode(
            title="Select SOP Node",
            node_type_filter=hou.nodeTypeFilter.Sop
        )
        if not path:
            return

        self.node_path_box.setText(path)
        # use the scope derived from the dropdown index
        scope = getattr(self, "run_over_scope", "points")
        attrs_block = self.get_attrs_block(path, scope)
        self.attrs_edit.setText(f"{attrs_block}")

    def find_attributes(self):
        path = self.node_path_box.text().strip()

        if not path:
            hou.ui.displayMessage("No Node Selected.\nClick 'Find Node' first.")
            return

        scope = getattr(self, "run_over_scope", "points")

        try:
            attrs_block = self.get_attrs_block(path, scope)
        except hou.Error as e:
            hou.ui.displayMessage(str(e))
            return
        self.attrs_edit.setText(attrs_block)

    def show_help(self):
        msg = (
            "GEN AI Wrangle – Help\n\n"
            "Overview:\n"
            "This tool uses an LLM (Gemini) to generate or fix VEX/Python code for\n"
            "Houdini, and to answer technical questions.\n\n"
            "Run Over:\n"
            "  - Controls what the VEX wrangle runs over (Detail, Primitives,\n"
            "    Points, Vertices). This is used both in the prompt and on the\n"
            "    created Attribute Wrangle node.\n\n"
            "Mode:\n"
            "  - Message Mode:\n"
            "      Ask general Houdini / VEX / Python questions. The model replies\n"
            "      with an explanation (and small code examples if useful).\n"
            "  - Create Code(VEX):\n"
            "      Generates a VEX snippet for an Attribute Wrangle based on your\n"
            "      prompt and the selected Run Over / Attributes / Node Path.\n"
            "  - Create Code(Python):\n"
            "      Generates Python using the 'hou' module to work inside Houdini.\n"
            "  - Code Fix(VEX):\n"
            "      Paste existing VEX into the 'Code' box, describe what you want\n"
            "      to change in the Prompt, and it will return an updated VEX snippet.\n"
            "  - Code Fix(Python):\n"
            "      Same as above, but for Houdini Python code.\n\n"
            "Attributes:\n"
            "  - 'Find Attributes' inspects the selected SOP node and lists its\n"
            "    attributes (with type and size). This context is passed to the LLM.\n"
            "  - 'Disable Attributes' ignores this list and tells the model that no\n"
            "    attribute information is provided.\n\n"
            "Node Path:\n"
            "  - 'Find Node' lets you pick a SOP node. Its path and attributes are\n"
            "    sent as context. When you create a node from the result, the new\n"
            "    wrangle / python node will be created in the same network, and will\n"
            "    connect its input to the chosen node if possible.\n\n"
            "Prompt:\n"
            "  - Describe what you want: behaviour, effect, or question.\n"
            "  - In Fix modes, this should describe how you want the pasted code\n"
            "    to be changed or what is currently broken.\n\n"
            "Code (Fix modes only):\n"
            "  - Visible only in Code Fix(VEX) and Code Fix(Python).\n"
            "  - Paste the existing code here; the model receives both the code\n"
            "    and your Prompt and returns an updated version.\n\n"
            "Bottom bar:\n"
            "  - Generate: send the prompt to the model.\n"
            "  - Code Commentary: when enabled, the model is allowed to add brief\n"
            "    comments explaining the code. When disabled, it is asked to output\n"
            "    code only.\n"
            "  - Clear: reset the UI back to defaults.\n"
            "  - ?: open this help window.\n\n"
            "Result window:\n"
            "  - Shows the raw LLM output.\n"
            "  - 'Copy Code' copies just the code block between <<<VEX>>>/<<<PYTHON>>>\n"
            "    and <<<END>>>.\n"
            "  - 'Create Node' creates an Attribute Wrangle or Python node from the\n"
            "    code (depending on the current Mode).\n"
            "  - 'OK' closes the result window.\n"
        )
        hou.ui.displayMessage(msg)


parent = hou.ui.mainQtWindow()
window = appUI(parent)
window.show()
window.raise_()
window.activateWindow()