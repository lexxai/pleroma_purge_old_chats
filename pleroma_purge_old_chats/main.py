try:
    import pleroma_purge_old_chats.purge_old_chats as pleroma_purge
except ImportError :
    import purge_old_chats as pleroma_purge


def cli():
    #global verbose_mode
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', type=int, nargs='?', default=0, const=1,
                        help='Detailed printing of the result of command execution.')
    parser.add_argument('-c', '--config',
                        help='path to config ini file')
    parser.add_argument('--demo', nargs='?', const=True,
                        help='Demo mode without real delete records')
    args = parser.parse_args()
    verbose_mode = bool(int(args.verbose))
    #vprint(args)
    if args.config is not None:
        if not os.path.isfile(args.config):
            print(f"config file '{args.config}' not found")
            exit(1)
        else:
            args.config = os.path.abspath(args.config)


    pleroma_purge.purge_old_messages(args.config, demo=args.demo, 
                                     verbose_mode=verbose_mode)

    #pleroma_purge.main()

if __name__ == '__main__':
    cli()
