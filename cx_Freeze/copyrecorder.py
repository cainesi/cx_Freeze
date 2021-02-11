# Code for tracing the reason why files have been included in freeze

from typing import Optional, Tuple, Dict, List, Set

class CopyReason:
    def __init__(self, explanation: str,
                 priorReason: Optional["CopyReason"] = None):
        self.explanation = explanation
        self.priorReason = priorReason
        return

class CopyRecorder:
    """Records data about why files are being included in the freeze."""
    def __init__(self):
        self.copy_dict: Dict[Tuple[str,str], CopyReason] = {}
        self.source_files: Dict[str, Set[str]] = {}  # list of sources from which file copied from
        self.destination_files: Dict[str, Set[str]] = {}  # list of destinations to which file copied
        # TODO: Add an option to log items to disk as they arise, so that the copying activity can be reviewed later, even following a crash.

        return

    def record_copied_file(self, srcPath: str, dstPath: str, reason: CopyReason):
        self.copy_dict[(srcPath, dstPath)] = reason
        if srcPath not in self.destination_files: self.destination_files[srcPath] = set()
        if dstPath not in self.source_files: self.source_files[dstPath] = set()
        return

    def destination_was_copied_to(self, dstPath: str) -> bool:
        if dstPath in self.source_files: return True
        return False

    def source_was_copied(self, srcPath: str) -> bool:
        if srcPath in self.destination_files: return True
        return False