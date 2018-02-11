#!/bin/python3

import os
import sys,itertools,copy

class Order(object):
    def __init__(self,order_id,timestamp,symbol,order_type,side,price,quantity):
        self.order_id = int(order_id)
        self.timestamp = timestamp
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.price = float(price)
        self.quantity = int(quantity)
    
    def __str__(self):
        return('%s : %s : %s : %s : %s : %s : %s'%(self.order_id,self.timestamp,self.symbol,self.order_type,self.side,self.price,self.quantity))
    
    def updateOrder(self):
        pass
    
    def partiallyCancelOrder(self):
        pass

class ValidOrders(object):
    def __init__(self,orders):
        self.orders = sorted(orders,key=lambda x : (x.symbol,x.side,x.price))
    
    def getOrderById(self,order_id):
        order = [o for o in self.orders if o.order_id == order_id]
        return order
        
    def addOrder(self,order):
        self.orders.append(order)
        self.orders = sorted(self.orders,key = lambda x: (x.symbol,x.side,x.price))
    
    def cancelOrder(self,order):
        idx = [i for i,o in enumerate(self.orders) if o.order_id == order.order_id]
        if idx:
            del self.orders[idx[0]]
            self.orders = sorted(self.orders,key = lambda x : (x.symbol,x.side,x.price))
            
    def helperMethod(self,orders):
        buy_orders = sell_orders = None
        for side,ordr in itertools.groupby(orders,key = lambda x : x.side):
            if side == 'B':
                buy_orders = copy.deepcopy(sorted(list(ordr),key = lambda x: x.price))
            elif side == 'S':
                sell_orders = copy.deepcopy(sorted(list(ordr),key = lambda x : x.price))
        return buy_orders,sell_orders
    
    def matchOrders(self,symbol=None):
        matches = []
        if symbol:
            orders_by_sm = [o for o in self.orders if o.symbol == symbol]
            buy_orders,sell_orders = self.helperMethod(orders_by_sm)
            matches = self.matcher(buy_orders,sell_orders) if buy_orders and sell_orders else []
        else:
            copy_ords = copy.deepcopy(self.orders)
            for symbol,ods in itertools.groupby(copy_ords,key=lambda x: x.symbol):
                buy_orders,sell_orders =  self.helperMethod(list(ods))
                if buy_orders and sell_orders:
                    matches_by_sym = self.matcher(buy_orders,sell_orders)
                    if matches_by_sym:
                        matches.extend(matches_by_sym)
        print('Match Result : ',matches)
        return sorted(matches)
                        
    def matcher(self,buy_orders,sell_orders):
        matches = []
        orders_ids = [o.order_id for o in buy_orders+sell_orders]
        total_combinations = []
        
        for bo in buy_orders:
            for so in sell_orders:
                total_combinations.append((bo,so))
        for bo,so in total_combinations:
            if bo.price >= so.price and bo.order_type == so.order_type:
                if bo.order_id not in [o.order_id for o in self.orders] or so.order_id not in [o.order_id for o in self.orders]:
                    continue
                
                if bo.quantity == so.quantity:
                    self.cancelOrder(bo)
                    self.cancelOrder(so)
                    mq = bo.quantity 
                elif so.quantity > bo.quantity:
                    self.cancelOrder(bo)
                    bordr = [o for o in self.orders if o.order_id ==  so.order_id][0]
                    bordr.quantity = so.quantity - bo.quantity
                    mq = bo.quantity
                elif bo.quantity > so.quantity:
                    self.cancelOrder(so)
                    bordr = [o for o in self.orders if o.order_id ==  bo.order_id][0]
                    bordr.quantity = bo.quantity - so.quantity
                    mq = so.quantity
                agreed_price = min(bo.price,so.price)
                matches.append('%s|%s,%s,%s,%s|%s,%s,%s,%s'%(bo.symbol,bo.order_id,bo.order_type,mq,agreed_price,agreed_price,mq,so.order_type,so.order_id))
        self.orders = sorted(self.orders,key = lambda x : (x.symbol,x.side))
        return matches
    
    def queryOrders(self,symbol,timestamp):
        current_state_of_matcher = []
        if symbol and timestamp:
            orders = [o for o in self.orders if int(o.timestamp)<= int(timestamp) and o.symbol == symbol ]
            orders = sorted(orders,key = lambda x : (x.symbol,x.side))
            buy_orders,sell_orders =  self.helperMethod(orders)
            current_state_of_matcher = ValidOrders.queryHelper(orders,buy_orders,sell_orders)
            
        elif symbol:
            orders = [o for o in self.orders if o.symbol == symbol ]
            orders = sorted(orders,key = lambda x : (x.symbol,x.side))
            buy_orders,sell_orders = self.helperMethod(orders)
            current_state_of_matcher = ValidOrders.queryHelper(orders,buy_orders,sell_orders)
            
        elif timestamp:
            orders = [o for o in self.orders if int(o.timestamp)<= int(timestamp) ]
            orders = sorted(orders,key = lambda x : (x.symbol,x.side))
            for sym,ods in itertools.groupby(orders,key=lambda x: x.symbol): 
                buy_orders,sell_orders = self.helperMethod(ods)
                current_state_of_matcher += ValidOrders.queryHelper(orders,buy_orders,sell_orders)
        else:
            orders = copy.deepcopy(self.orders)
            orders = sorted(orders,key = lambda x : (x.symbol,x.side))
            for sym,ods in itertools.groupby(orders,key=lambda x: x.symbol): 
                #print(sym)
                buy_orders,sell_orders = self.helperMethod(list(ods))
                current_state_of_matcher += ValidOrders.queryHelper(orders,buy_orders,sell_orders)
        #print('Query Result : ',current_state_of_matcher)
        return current_state_of_matcher
    
    @staticmethod
    def queryHelper(orders,buy_orders,sell_orders):
        matches = []
        copy_orders = copy.deepcopy(orders)
        if buy_orders and sell_orders:
            combinations = []
            matched_order_ids = []
            for bo in buy_orders:
                for so in sell_orders:
                    combinations.append((bo,so))
            for bo,so in combinations:
                if bo.price >= so.price and bo.order_type==so.order_type:
                    if bo.order_id not in [o.order_id for o in copy_orders] or so.order_id not in [o.order_id for o in copy_orders]:
                        continue
                    if bo.quantity == so.quantity:
                        copy_orders = [o for o in copy_orders if o.order_id!=bo.order_id]
                        copy_orders = [o for o in copy_orders if o.order_id!=so.order_id]
                        mbq = msq = bo.quantity 
                    elif bo.quantity > so.quantity:
                        copy_orders = [o for o in copy_orders if o.order_id!=bo.order_id]
                        copy_orders = [o for o in copy_orders if o.order_id!=so.order_id]
                        msq = so.quantity
                        mbq = bo.quantity
                    elif so.quantity > bo.quantity:
                        copy_orders = [o for o in copy_orders if o.order_id!=so.order_id]
                        copy_orders = [o for o in copy_orders if o.order_id!=bo.order_id]
                        mbq = bo.quantity
                        msq = so.quantity
                    matches.append('%s|%s,%s,%s,%s|%s,%s,%s,%s'%(bo.symbol,bo.order_id,bo.order_type,mbq,bo.price,so.price,msq,so.order_type,so.order_id))
            #if copy_orders:
            #    for side,ords in itertools.groupby(copy_orders,key=lambda x: x.side):
            #        matches.extend('%s|%s,%s,%s,%s|'%(o.symbol,o.order_id,o.order_type,o.quantity,o.price) if side=='B' else '%s||%s,%s,%s,%s'%(o.symbol,o.price,o.quantity,o.order_type,o.order_id) for o in ords)
            
        elif buy_orders:
            matches += ['%s|%s,%s,%s,%s|'%(o.symbol,o.order_id,o.order_type,o.quantity,o.price) for o in buy_orders]
        elif sell_orders:
            matches += ['%s||%s,%s,%s,%s'%(o.symbol,o.price,o.quantity,o.order_type,o.order_id) for o in sell_orders]
        #print(len(matches))
        #print(matches)
        return matches[:5]  if len(matches)>5 else matches      
    
    

def processQueries(queries):
    # Write your code here.
    split_queries = [query.split(',') for query in queries] 
    results = []
    valid_orders = ValidOrders([])
    for i,query in enumerate(split_queries):
        if query[0]=='N':
            ## Logic for New Orders...
            valid_order = True if query[1].isdigit() and query[2].isdigit() and query[3].isalpha() and query[4]in ['M','L','I'] and query[5] in ['B','S'] and '.' in query[6] and query[7].isdigit() else False
            dupe_order = True if [o for o in valid_orders.orders if o.order_id==int(query[1])] else False
            if not dupe_order and valid_order:
                valid_orders.addOrder(Order(*query[1:]))
                results.append('%s - Accept'%query[1])
            else:
                results.append('%s - Reject - 303 - Invalid order details'%query[1])
                
        elif query[0]=='A':
            ## Logic for Amend Orders
            existing_order = [o for o in valid_orders.orders if o.order_id==int(query[1])]
            if existing_order:
                o = existing_order[0]
                if int(o.timestamp) < int(query[2]) and o.symbol ==  query[3] and o.order_type == query[4] and o.side == query[5] and '.' in query[6] and query[7].isdigit():
                    o.price = float(query[6])
                    o.quantity = int(query[7])
                    results.append('%s - AmendAccept'%query[1])
                else:
                    results.append('%s - AmendReject - 101 - Invalid amendment details'%query[1])
            else:
                results.append('%s - AmendReject - 404 - Order does not exist'%query[1])
            
        elif query[0]=='X':
            ## Logic to Cancel Order.. Partial Cancel Allowed.. But handling pending
            existing_order = [o for o in valid_orders.orders if o.order_id==int(query[1])]
            if existing_order:
                o = existing_order[0] 
                if int(o.timestamp) < int(query[2]):
                    valid_orders.cancelOrder(o)
                    results.append('%s - CancelAccept'%query[1])
                else:
                    results.append('%s - CancelReject - 404 - Order does not exist'%query[1])    
            else:
                results.append('%s - CancelReject - 404 - Order does not exist'%query[1])
        elif query[0]=='M':
            results.extend(valid_orders.matchOrders(query[2] if len(query) == 3 else None))
        elif query[0]=='Q':
            symbol,timestamp = (None,query[1]) if len(query[1:]) == 1 and query[1].isdigit() else (query[1],None) if len(query[1:])==1 and query[1].isalpha() else (query[2],query[1]) if len(query[1:])==2 and query[1].isdigit() else (query[1],query[2]) if len(query[1:])==2 and query[1].isalpha() else (None,None)
            results.extend(valid_orders.queryOrders(symbol,timestamp))
    return results


if __name__ == '__main__':
    f = open(os.environ['OUTPUT_PATH'], 'w')

    queries_size = int(input())

    queries = []
    for _ in range(queries_size):
        queries_item = input()
        queries.append(queries_item)

    response = processQueries(queries)

    f.write("\n".join(response))

    f.write('\n')

    f.close()

