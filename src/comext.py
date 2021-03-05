# from pyathena import connect
import pandas as pd
import time
import sqlite3


class COMEXTParser:
    def __init__(self):
        self.conn = sqlite3.connect("../datasets/comext.db")

    def get_data_as_df(
        self,
        declarant=None,
        partner=None,
        trade_type=None,
        flow=None,
        time_period=None,
        hs6=None,
        limit=None,
    ):
        """
        declarant: The Declarant (or reporting country) is the country compiling
        and sending data to Eurostat. As a general principle, Member States
        should record an import when goods enter their statistical
        territory  and  an  export  when  goods leave that  territory,
        except  if those  goods  are  in  simple transit.
        Goods  should  be  recorded  only  when  adding  to  or
        subtracting  from  the  stock  of national material
        resources or, in the context of extra-EU trade, when
        customs formalities are applied.

        partner: The partner country is the last known country
        of destination for exports, the country of origin
        for imports from non-EU countries and the country
        of consignment for imports from Member States.
        The  partner  can  be a EU Member  State,  a
        non-EU  country  or  a  geo-economic  area.

        trade_type ("I", "E"): International trade in goods statistics (ITGS)
        are based on intra-EU and extra-EU trade.
        Intra-EUtrade (type  I) deals  with  the trade  in  goods  between EU Member
        States,  extra-EU  trade (type E) with the trade in goods with non-EU countries.

        time_period, str like '201805': This code refers to the reference period:
        When the customs declaration is the source for records on
        imports and exports, the reference period is  the
        calendar  year  and  month  when  the  declaration
        is  accepted  by the customs authorities.
        Within the Intrastat system, the reference period
        is in principle the calendar month of  import  or
        export  of  the  goodsor,  for  sales  and  purchases,
        the  calendar  month  when  the chargeable  event  for
        VAT  purposes  occurs. The  chargeable  event  relates
        to  the  issue  date  of the invoice.

        flow (1, 2): The  flow  can  be  an  import (1) or an export(2).
        Except  for  some  specific  goods,like  vessels and aircraft,
        International trade in goods statistics follow the physical
        movement of the goods. Member  States  record an  import  when
        goods  enter  their  statistical  territory  and  an
        export when goods leave that territory except if those goods
        are in simple transit.

        product_nc: Product code in hs taxonomy



        """
        query = "SELECT declarant_iso,partner_iso,trade_type,product_nc,flow,period,value_in_euros,quantity_in_kg FROM comext WHERE 1=1 "

        if time_period is not None:
            query += "AND period='{}' ".format(time_period)
        if hs6 is not None:
            query += "AND product_nc LIKE '{}%' ".format(hs6)
        if declarant is not None:
            query += "AND declarant='{}' ".format(declarant)
        if partner is not None:
            query += "AND partner='{}' ".format(partner)
        if trade_type is not None:
            query += "AND trade_type='{}' ".format(trade_type)

        if limit is not None:
            query += " LIMIT {}".format(limit)

        print(query)
        df = pd.read_sql(query, self.conn)
        return df

    def get_data_as_df_for_period_range(
        self,
        time_period_start,
        time_period_end,
        hs6,
        limit=None,
    ):
        query = "SELECT declarant_iso,partner_iso,trade_type,product_nc,flow,period,value_in_euros,quantity_in_kg FROM comext WHERE 1=1 "

        query += "AND period BETWEEN '{}' AND '{}' ".format(time_period_start, time_period_end)
        query += "AND product_nc LIKE '{}%' ".format(hs6)

        if limit is not None:
            query += " LIMIT {}".format(limit)

        print(query)
        df = pd.read_sql(query, self.conn)
        return df


    def __del__(self):
        self.conn.close()


def demo():
    comext_parser = COMEXTParser()
    #df = comext_parser.get_data_as_df(limit=100)
    t1 = time.time()
    #df = comext_parser.get_data_as_df(declarant="FR", partner="NL", time_period="201008")
    df = comext_parser.get_data_as_df(time_period="202008", hs6="901831")
    print(time.time() - t1)

    bb = 1


if __name__ == "__main__":
    demo()
