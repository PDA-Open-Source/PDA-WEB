import logging
import os
import logstash
from decouple import config

home = os.path.expanduser("~")
PATH = os.path.join(home, "Logs")
logstash_info_handler = logstash.TCPLogstashHandler(host=config('LOGSTASH_HOST'), port=config('LOGSTASH_PORT'), version=1, message_type='socion-staging-web-app')
logstash_info_handler.setLevel(logging.INFO)
logstash_error_handler = logstash.TCPLogstashHandler(host=config('LOGSTASH_HOST'), port=config('LOGSTASH_PORT'), version=1, message_type='socion-staging-web-app')
logstash_error_handler.setLevel(logging.ERROR)

"""Info/Error Logging for CORE APP!!"""
core_logger = logging.getLogger('CORE APP LOGS')
core_logger.setLevel(logging.INFO)

LOGS_PATH = '%s%s' % (PATH, '/CORE-APP.log')
core_log_file_handler = logging.FileHandler(LOGS_PATH)
core_log_file_handler.setLevel(logging.INFO)

core_log_stream_handler = logging.StreamHandler()
core_log_stream_handler.setLevel(logging.ERROR)

core_log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

core_log_file_handler.setFormatter(core_log_formatter)
core_log_stream_handler.setFormatter(core_log_formatter)

core_logger.addHandler(core_log_file_handler)
core_logger.addHandler(core_log_stream_handler)
core_logger.addHandler(logstash_info_handler)
core_logger.addHandler(logstash_error_handler)


"""Info/Error Logging for Attestation APP!!"""
attestation_logger = logging.getLogger('ATTESTATION APP LOGS')
attestation_logger.setLevel(logging.INFO)

LOGS_PATH = '%s%s' % (PATH, '/ATTESTATION-APP.log')
attestation_log_file_handler = logging.FileHandler(LOGS_PATH)
attestation_log_file_handler.setLevel(logging.INFO)

attestation_log_stream_handler = logging.StreamHandler()
attestation_log_stream_handler.setLevel(logging.ERROR)

attestation_log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

attestation_log_file_handler.setFormatter(attestation_log_formatter)
attestation_log_stream_handler.setFormatter(attestation_log_formatter)

attestation_logger.addHandler(attestation_log_file_handler)
attestation_logger.addHandler(attestation_log_stream_handler)
attestation_logger.addHandler(logstash_info_handler)
attestation_logger.addHandler(logstash_error_handler)


"""Info/Error Logging for Authentication APP!!"""
authentication_logger = logging.getLogger('AUTHENTICATION APP LOGS')
authentication_logger.setLevel(logging.INFO)

LOGS_PATH = '%s%s' % (PATH, '/AUTHENTICATION-APP.log')
authentication_log_file_handler = logging.FileHandler(LOGS_PATH)
authentication_log_file_handler.setLevel(logging.INFO)

authentication_log_stream_handler = logging.StreamHandler()
authentication_log_stream_handler.setLevel(logging.ERROR)

authentication_log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

authentication_log_file_handler.setFormatter(authentication_log_formatter)
authentication_log_stream_handler.setFormatter(authentication_log_formatter)

authentication_logger.addHandler(authentication_log_file_handler)
authentication_logger.addHandler(authentication_log_stream_handler)
authentication_logger.addHandler(logstash_info_handler)
authentication_logger.addHandler(logstash_error_handler)


"""Info/Error Logging for Entity APP!!"""
entity_logger = logging.getLogger('ENTITY APP LOGS')
entity_logger.setLevel(logging.INFO)

LOGS_PATH = '%s%s' % (PATH, '/ENTITY-APP.log')
entity_log_file_handler = logging.FileHandler(LOGS_PATH)
entity_log_file_handler.setLevel(logging.INFO)

entity_log_stream_handler = logging.StreamHandler()
entity_log_stream_handler.setLevel(logging.ERROR)

entity_log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

entity_log_file_handler.setFormatter(entity_log_formatter)
entity_log_stream_handler.setFormatter(entity_log_formatter)

entity_logger.addHandler(entity_log_file_handler)
entity_logger.addHandler(entity_log_stream_handler)
entity_logger.addHandler(logstash_info_handler)
entity_logger.addHandler(logstash_error_handler)


"""Info/Error Logging for Program APP!!"""
program_logger = logging.getLogger('PROGRAM APP LOGS')
program_logger.setLevel(logging.INFO)

LOGS_PATH = '%s%s' % (PATH, '/PROGRAM-APP.log')
program_log_file_handler = logging.FileHandler(LOGS_PATH)
program_log_file_handler.setLevel(logging.INFO)

program_log_stream_handler = logging.StreamHandler()
program_log_stream_handler.setLevel(logging.ERROR)

program_log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

program_log_file_handler.setFormatter(program_log_formatter)
program_log_stream_handler.setFormatter(program_log_formatter)

program_logger.addHandler(program_log_file_handler)
program_logger.addHandler(program_log_stream_handler)
program_logger.addHandler(logstash_info_handler)
program_logger.addHandler(logstash_error_handler)
