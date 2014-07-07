import pstats
p = pstats.Stats('calc.profile')
p.strip_dirs().sort_stats('cumulative').print_stats()
