class UrlNotFound(Exception):
    pass

class SyncFailed(Exception):
    pass

class UrlFileNotFound(SyncFailed):
    pass

class UrlFileRecoveryFailed(SyncFailed):
    pass

class UrlFileInvalidJSON(SyncFailed):
    pass

class UrlFileInvalidSchema(SyncFailed):
    pass

class SyncDbError(SyncFailed):
    pass