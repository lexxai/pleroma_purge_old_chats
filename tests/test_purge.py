import sys
try:
    sys.path.append("./")  
    import pleroma_purge_old_chats.purge_old_chats as pleroma_purge
except ImportError :
    sys.path.append("../")  
    import pleroma_purge_old_chats.purge_old_chats as pleroma_purge


pleroma_purge.main()
