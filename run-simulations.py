from simulate import *

rs001 = RandomServer(1)
rs005 = RandomServer(5)
rs010 = RandomServer(10)

fs001 = FixedServer([1])
fs005 = FixedServer(range(1-5))
fs010 = FixedServer(range(1-10))

fc010_rs001 = FixedCheckingClient(rs001, 10)
fc010_rs005 = FixedCheckingClient(rs005, 10)
fc010_rs010 = FixedCheckingClient(rs010, 10)

lc050005002_rs001 = LinearServerBasedClient(rs001, 50, 5, 2)
lc050005002_rs005 = LinearServerBasedClient(rs005, 50, 5, 2)
lc050005002_rs010 = LinearServerBasedClient(rs010, 50, 5, 2)

ec100005500_rs001 = ExponentialServerBasedClient(rs001, 50, 5, .5)
ec100005500_rs005 = ExponentialServerBasedClient(rs005, 50, 5, .5)
ec100005500_rs010 = ExponentialServerBasedClient(rs010, 50, 5, .5)

times = 100000
run_sim(fc010_rs001, times)
run_sim(fc010_rs005, times)
run_sim(fc010_rs010, times)
run_sim(lc050005002_rs001, times)
run_sim(lc050005002_rs005, times)
run_sim(lc050005002_rs010, times)
run_sim(ec100005500_rs001, times)
run_sim(ec100005500_rs005, times)
run_sim(ec100005500_rs010, times)





