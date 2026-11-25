"""One prompt of a chat and what the agent did after it."""


class Turn:
    """One prompt of the user and what the assistant did after it."""

    def __init__(self, time, prompt):
        # When the user sent the prompt, as an ISO 8601 string.
        self.time = time
        self.prompt = prompt
        # The last text the assistant wrote in this turn.
        self.reply = ""
        # What the turn ended on: "text", a tool name, or "" when nothing came.
        self.last_block = ""
        # Files edited or written, in the order first touched.
        self.files = []
        # Every text the assistant wrote, and a (tool, argument) pair for every tool call, in order, for --full.
        self.steps = []
        # Every text the assistant wrote, for --search --replies.
        self.texts = []

    def add_text(self, text):
        self.reply = text
        self.last_block = "text"
        self.steps.append(text)
        self.texts.append(text)

    def add_call(self, tool, arg, changed_file=None):
        """Records a call of `tool`; `arg` is its most telling input, `changed_file` the file it edits."""
        self.last_block = tool
        self.steps.append((tool, arg))
        if changed_file and changed_file not in self.files:
            self.files.append(changed_file)
