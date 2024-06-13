import pstats

stats = pstats.Stats("profile/my_profile.prof")
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats(50)
