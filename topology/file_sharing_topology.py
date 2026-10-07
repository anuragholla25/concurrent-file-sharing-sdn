from mininet.topo import Topo


class FileSharingTopo(Topo):

    def build(self):

        # One Open vSwitch
        s1 = self.addSwitch(
            's1',
            protocols='OpenFlow13'
        )

        # Three clients
        h1 = self.addHost(
            'h1',
            ip='10.0.0.1/24'
        )

        h2 = self.addHost(
            'h2',
            ip='10.0.0.2/24'
        )

        h3 = self.addHost(
            'h3',
            ip='10.0.0.3/24'
        )

        # One server
        h4 = self.addHost(
            'h4',
            ip='10.0.0.4/24'
        )

        # Connect all hosts to the switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)


topos = {
    'filesharing': FileSharingTopo
}
