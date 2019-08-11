"""
Functions for interacting with the computable protocol
"""
import os
import logging.config
from time import sleep, time
from web3 import Web3
from computable.contracts import Datatrust, Voting
from computable.helpers.transaction import call, send

import constants
import settings

LOGGING_CONFIG = os.path.join(settings.ROOT_DIR, 'logging.conf')
logging.config.fileConfig(LOGGING_CONFIG)
log = logging.getLogger()

class Protocol():
    """
    Class to manage all interactions with the deployed contracts
    """
    def __init__(self):
        self.datatrust = None
        self.voting = None

    def init_protocol(self, rpc_path, datatrust_contract, datatrust_host, voting_contract, datatrust_key, datatrust_wallet):
        """
        :param rpc_path: URL to the RPC provider for the network
        :param datatrust_contract: Deployed address of the datatrust contract
        :param datatrust_host: URL of this application. Used to submit self as datatrust
        :param voting_contract: Deployed address of voting contract
        :param datatrust_key: Private key for wallet
        :param datatrust_wallet: Wallet address
        """
        self.w3 = self.initialize_web3(rpc_path)
        self.datatrust_contract = datatrust_contract
        self.datatrust_host = datatrust_host
        self.voting_contract = voting_contract
        self.datatrust_key = datatrust_key
        self.datatrust_wallet = datatrust_wallet

    def initialize_web3(self, rpc_path):
        """
        Setup the web3 provider
        """
        w3 = Web3(Web3.HTTPProvider(rpc_path))
        log.info('w3 provider set')
        return w3

    def initialize_datatrust(self):
        """
        Confirm or create role as datatrust backend in protocol
        """
        log.info('Getting current datatrust address from network')
        self.datatrust = Datatrust(self.datatrust_wallet)
        self.datatrust.at(self.w3, self.datatrust_contract)
        self.voting = Voting(self.datatrust_wallet)
        self.voting.at(self.w3, self.voting_contract)

        datatrust_hash = self.w3.sha3(text=self.datatrust_host)
        if self.get_backend_address():
            log.info('This server is the datatrust host. Resolving registration')
            resolve = send(
                self.w3, 
                self.datatrust_key, 
                self.datatrust.resolve_registration(
                    self.w3.sha3(text=self.datatrust_host)
                    )
                )
            log.info(f'Resolved, transaction id: {resolve}')
        else:
            # backend not set, or is set to a different host
            datatrust_url = call(self.datatrust.get_backend_url())
            is_candidate = call(self.voting.is_candidate(datatrust_hash))
            candidate_is = call(self.voting.candidate_is(datatrust_hash, constants.PROTOCOL_REGISTRATION))
            if datatrust_url == self.datatrust_host:
                log.info('Server has been registered as datatrust, but not voted in')
            elif is_candidate and candidate_is:
                log.info('This datatrust is a candidate but has not been voted in')
                poll_status = call(self.voting.poll_closed(datatrust_hash))
                if poll_status:
                    log.info('This datatrust was a candidate, but was not voted in before the poll closed')
                    resolve = send(
                        self.w3, 
                        self.datatrust_key, 
                        self.datatrust.resolve_registration(datatrust_hash)
                        )
                    log.info(f'Resolved any prior registration, transaction id: {resolve.hex()}')
                    self.wait_for_mining(resolve)
                    register = self.register_host()
                    log.info(f'Datatrust has been registered.')
                else:
                    log.info('This datatrust is a candidate. Voting polls are still open.')
            else:
                log.info('No backend or different host set. Resolving prior registrations and Submitting this one for voting')
                resolve = send(
                    self.w3, 
                    self.datatrust_key, 
                    self.datatrust.resolve_registration(datatrust_hash)
                    )
                log.info(f'Resolved any prior registration, transaction id: {resolve.hex()}')
                self.wait_for_mining(resolve)
                register = self.register_host()

    def get_backend_address(self):
        """
        Return True if the Ethereum address for the voted-in datatrust is this datatrust
        """
        backend = call(self.datatrust.get_backend_address())
        if backend == self.datatrust_wallet:
            return True
        else:
            return False

    def wait_for_vote(self):
        """
        Check if this backend is registered as the datatrust
        """
        is_host = False
        while is_host == False:
            backend = call(self.datatrust.get_backend_url())
            if backend != self.datatrust_host:
                print('backend not voted in yet, waiting for votes...')
                sleep(30)
            else:
                is_host = True
        return True

    def register_host(self):
        """
        Register a host as the datatrust in protocol
        """
        log.info('****Registering host****')
        register = send(self.w3, self.datatrust_key, self.datatrust.register(self.datatrust_host))
        self.wait_for_mining(register)
        voting = Voting(self.datatrust_wallet)
        voting.at(self.w3, self.voting_contract)
        datatrust_hash = self.w3.sha3(text=self.datatrust_host)
        is_registered = call(voting.is_candidate(datatrust_hash))
        if is_registered:
            log.info(f'Backend registered. Voting is now open.')
        else:
            log.error('Host attempted to register but did not succeed')

    def send_data_hash(self, listing, data_hash):
        """
        On a successful post to the API db, send the data hash to protocol
        """
        if self.get_backend_address():   
            receipt = send(self.w3, self.datatrust_key, self.datatrust.set_data_hash(listing, data_hash))
            return receipt
        else:
            log.critical(constants.NOT_DATATRUST)
            raise ValueError(constants.NOT_DATATRUST)

    def wait_for_mining(self, tx):
        """
        Wait for a transaction to be mined before proceeding
        :param tx: Transaction receipt
        """
        is_mined = self.w3.eth.getTransactionReceipt(tx.hex())
        while is_mined is None:
                    log.info('Transaction has not been mined, going to sleep')
                    sleep(15)
                    is_mined = self.w3.eth.getTransactionReceipt(tx.hex())

    def create_file_hash(self, data):
        """
        Return a sha3 hash for the file provided
        :param data: The file object to hash
        :return: sha3 hash of file contents
        :return type: string
        """
        sha3_hash = None
        with open(data, 'rb') as file_contents:
            b = file_contents.read(1024*1024) # read file in 1MB chunks
            while b:
                sha3_hash = self.w3.sha3(b)
                b = file_contents.read(1024*1024)
        return sha3_hash

    def validate_candidate(self, listing_hash):
        """
        Verify a candidate has been submitted to Computable Protocol
        by parsing logs for 'CandidateAdded' event and matching listing hash
        Verify voteBy has not expired
        :params listing_hash: String listing hash for listing
        :return owner address if valid otherwise return None:
        :return type string:
        """
        owner = None
        voting_filter = self.voting.deployed.eventFilter(
            constants.CANDIDATE_ADDED,{'fromBlock':0,'toBlock':'latest'}
        )
        events = voting_filter.get_all_entries()
        for evt in events:
            event_hash = '0x' + evt['args']['hash'].hex()
            print(f'Comparing event hash {event_hash} to listing hash {listing_hash}')
            if event_hash == listing_hash:
                log.info(f'Listing {listing_hash} has been listed as a candidate in protocol')
                voteBy = evt['args']['voteBy']
                if voteBy > int(time.time()):
                    owner = evt['args']['owner']
        return owner


deployed = Protocol()
