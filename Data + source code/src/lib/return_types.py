__all__ = ['ReturnTypes']


class ReturnTypes(object):
    TOTAL_RETURN = 'TR'
    EXCESS_RETURN = 'ER'
    NET_TOTAL_RETURN = 'NTR'

    @staticmethod
    def is_total_return(return_type):
        return 'Total Return' in return_type

    @staticmethod
    def is_excess_return(return_type):
        return 'Excess Return' == return_type

    @staticmethod
    def convert_return_type(return_type):
        if ReturnTypes.is_total_return(return_type):
            return ReturnTypes.TOTAL_RETURN
        if ReturnTypes.is_excess_return(return_type):
            return ReturnTypes.EXCESS_RETURN
        return None
