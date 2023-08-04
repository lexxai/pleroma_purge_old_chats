try:
    from .purge_old_chats import purge_old_messages
except ImportError :
     from purge_old_chats import purge_old_messages
import argparse
import os
import sys
if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

def cli():
    #global verbose_mode
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', type=int, nargs='?', default=0, const=1,
                        help='Detailed printing of the result of command execution.')
    parser.add_argument('-c', '--config',
                        help='path to config ini file')
    parser.add_argument('--demo', nargs='?', const=True,
                        help='Demo mode without real delete records')
    parser.add_argument('--version', nargs='?', const=True,
                        help='show version')                        
    args = parser.parse_args()
    verbose_mode = bool(int(args.verbose))
    #vprint(args)
    if args.config is not None:
        if not os.path.isfile(args.config):
            print(f"config file '{args.config}' not found")
            exit(1)
        else:
            args.config = os.path.abspath(args.config)

    if args.version is not None:
        print("Version:",version('pleroma_purge_old_chats'),__package__)
        return

    purge_old_messages(args.config, demo=args.demo, 
                                     verbose_mode=verbose_mode)


if __name__ == '__main__':
    cli()
