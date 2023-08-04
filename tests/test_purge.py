import sys
try:
    sys.path.append("./")  
    from pleroma_purge_old_chats import main as m
except ImportError :
    sys.path.append("../")  
    from pleroma_purge_old_chats import main as m

if __name__ == '__main__':
    m.cli()
