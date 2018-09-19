import logging
from dns import resolver, reversename, exception
from ..utils.settings import data, collect


def verify(item, dns_config, server_ip):
    try:
        res = resolver.Resolver()
        res.lifetime = 2.0
        res.nameservers = [server_ip]
        try:
            ip = str(res.query(item[0])[0].address)
        except resolver.NXDOMAIN as e:
            logging.warning("DNS service test server {} found no IP entry for {}: "
                            "{}".format(server_ip, item[0], e))
            return False
        try:
            hostname = str(res.query(
                reversename.from_address(item[1]), 'PTR'
            )[0].target)[:-1]
        except resolver.NXDOMAIN as e:
            logging.warning("DNS service test server {} found no hostname entry for {}: "
                            "{}".format(server_ip, item[1], e))
            return False
        if dns_config.get('hostnames').get(item[0]) == ip and item[0] == hostname:
            return True
        else:
            logging.warning("DNS service test server {} got {} using {}, "
                            "which differ from the configs entry {} when using "
                            "{}".format(server_ip, hostname, item[1], item[0], item[1]))
            return False
    except exception.Timeout as e:
        logging.warning("DNS service test timed out, {} server was unable to query {}: "
                        "{}".format(server_ip, item[1], e))
        return False
    except Exception as e:
        logging.exception("Ran into error trying to verify DNS addresses and hostnames: "
                          "{}".format(e))
        return False


@collect(data.get('services').get('dns').get('enabled'))
def dns(config):
    # Start the test as failure, it must be proven that the service works
    outcome = 0

    # Get the dns settings in the config, it is from main.json
    dns_config = config.get('services').get('dns')

    # Get the the pairs in a list [("webcse.csee.usf.edu", "131.247.3.5"), ...]
    hostname_ip_pairs = [(key, value) for key, value in
                         dns_config.get("hostnames").items()]

    # Test the list of pairs on each DNS Server given by looping over each one
    for server_tier, server_ip in dns_config.get('servers').items():
        # Use the verify function to verify that the hostname and IP Address are correct
        for pair in hostname_ip_pairs:
            if not verify(pair, dns_config, server_ip):
                # No point on continuing to test since it didn't pass one of the first
                # checks, return a failure
                return 0

    # If the service test got to this part it has not failed verification
    return 1
