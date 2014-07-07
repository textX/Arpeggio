import pstats
p = pstats.Stats('test_speed.profile')
p.strip_dirs().sort_stats('cumulative').print_stats()
