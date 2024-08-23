from config.parameter import LoggerParam
from src.util.tools import get_logger

sys_log = get_logger('system', fileName='system.log', stream=True)
error_log = get_logger('error', fileName='error.log', stream=True)


backup_recv_raw_log = get_logger('recv_raw', fileName='receive_raw.csv', backup_data=True, working=LoggerParam.backup_send_raw and LoggerParam.backup)
backup_send_raw_log = get_logger('send_raw', fileName='send_raw.csv', backup_data=True, working=LoggerParam.backup_send_raw and LoggerParam.backup)
backup_recv_log = get_logger('recv_data', fileName='receive_data.csv', backup_data=True, working=LoggerParam.backup_send_raw and LoggerParam.backup)
backup_send_log = get_logger('send_data', fileName='send_data.csv', backup_data=True, working=LoggerParam.backup_send_raw and LoggerParam.backup)
