# GUI controller containing all functions
import controller as control


def main():
    control.root.mainloop()


# Run main GUI application
if __name__ == '__main__':
    # Starting the GUI program
    main()

    # Profiling main function
    # import cProfile
    # import pstats
    #
    # profile = cProfile.Profile()
    # profile.runcall(main)
    # ps = pstats.Stats(profile)
    # ps.print_stats()

