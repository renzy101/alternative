
from project import app,db,bcrypt
from datetime import datetime, timedelta
from random import randint
import os
import base64
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.declarative import declarative_base, declared_attr
import jwt
import json
from urlparse import parse_qs, parse_qsl
from jwt import DecodeError, ExpiredSignature
import requests
from urllib import urlencode
from flask import Flask, g, send_file, request, redirect, url_for, jsonify,session


def create_token(user):
        payload = {
            'sub': user.userid,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=14)}
        token = jwt.encode(payload, app.config['TOKEN_SECRET'])
        return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['TOKEN_SECRET'])


def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.headers.get('Authorization'):
                response = jsonify(message='Missing authorization header')
                response.status_code = 401
                return response

            try:
                payload = parse_token(request)
            except DecodeError:
                response = jsonify(message='Token is invalid')
                response.status_code = 401
                return response
            except ExpiredSignature:
                response = jsonify(message='Token has expired')
                response.status_code = 401
                return response

            g.user_id = payload['sub']

            return f(*args, **kwargs)

        return decorated_function


class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True,nullable=False)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), nullable=False)
    
    
    def __init__(self ,userid,username,email,password):
        self.userid=userid
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password)

    def to_json(self):
        return dict(userid=self.userid,username=self.username,
                    email=self.email)


    @hybrid_property
    def get_username(self):
        return self.username

    @hybrid_property
    def get_email(self):
        return self.email


    @hybrid_property
    def get_password(self):
        return self.password

    


    def login(email,password):
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password,password):
            response = jsonify({"error":"1","data":{},"message":'failed'})
            response.status_code = 401
        else:
            token = create_token(user) 
            response = jsonify(token=token,information={"error":"null","data":{'token':token,'user':{'id':user.userid,'email': user.email,'name':user.username},"message":"Success"}})
        return response


    def register(username,email,password):
        json_data = request.json
        user = User(
             userid = randint(620000000,620099999),
             username=username,
             email=email,
             password=password)
        if user:
            db.session.add(user)
            db.session.commit()
            token = create_token(user)
            response = jsonify(token=token,information={"error":"null","data":{'token':token,'expires': "today",'user':{'id':user.userid,'email': user.email,'name':user.username},"message":"Success"}})
        else:
            response = jsonify({"error":"1","data":{},"message":'failed'})
        return response

class Account(User):
    __tablename__ = 'account'
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'),primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'account','inherit_condition': (userid == User.userid)}
    firstname = db.Column(db.String(120),nullable = False)
    lastname = db.Column(db.String(120),nullable = False)
    shippingAddress = db.Column(db.String(120),nullable = False)
    phoneNumber = db.Column(db.String(20),nullable=False)
    paymentMethod = db.Column(db.String(40),nullable=False)

    def __init__(self,userid,firstname,lastname,shippingAddress,phoneNumber,paymentMethod):
        self.userid = userid
        self.firstname = firstname
        self.lastname = lastname
        self.shippingAddress = shippingAddress
        self.phoneNumber = phoneNumber
        self.paymentMethod = paymentMethod

    @hybrid_property
    def get_userid(self):
        return self.userid

    @hybrid_property
    def get_firstname(self):
        return self.firstname

    @hybrid_property
    def get_lastname(self):
        return self.lastname

    @hybrid_property
    def get_shippingAddress(self):
        return self.shippingAddress

    @hybrid_property
    def get_phoneNumber(self):
        return self.phoneNumber

    @hybrid_property
    def get_paymentMethod(self):
        return self.paymentMethod

   

    def getOrders(userid):
        account = db.session.query(Account).filter_by(userid=userid).first()
        orders = db.session.query(Order).filter_by(user_id=account.userid).all()
        orderList = []
        for order in orders:
            orders.append({"orderDate":order.orderDate,"deliveryDate":order.deliveryDate,"oderStatus":order.orderStatus,"total":order.total,"items":order.Items})
        if(len(orderList)>0):
            response = jsonify({"error":"null","data":{"wishes":orderList},"message":"Success"})
        else:
            response = jsonify({"error":"1","data":{},"message":"No such orders exists"})
        return orderList
    
    def updateOrders(self):
        return True

    def checkout(self):
        return True

    def makeComplaint(message,userid):
        complaint = Complaint(
            userid = userid,
            message = message)
        db.session.add(complaint)
        db.session.commit()
        return jsonify({"message":"Success"})


    def chargePaymentMethod(self):
        pass

class Complaint(db.Model):
    __tablename__ = 'complaint'
    userid = db.Column(db.Integer,db.ForeignKey("user.userid"),nullable=False)
    message = db.Column(db.String(200),nullable=False)

class Address(db.Model):
    __tablename__ = 'address'
    userid = db.Column(db.Integer,db.ForeignKey('user.userid'),nullable=False)
    streetAddress = db.Column(db.String(80),nullable=False)
    city = db.Column(db.String(80),nullable=False)
    parrish = db.Column(db.String(20),nullable=False)
    postalCode = db.Column(db.String(20),nullable=False)

    User = db.relationship('User', primaryjoin='Address.user_id==User.id',
            backref=db.backref('Address'))
        
    def __init__(self,userid,streetAddress,city,parrish,postalCode):
        self.userid = userid
        self.streetAddress = streetAddress
        self.city = city
        self.parrish = parrish
        self.postalCode = postalCode


    @hybrid_property
    def get_streetAddress(self):
        return self.streetAddress

    @hybrid_property
    def get_city(self):
        return self.city

    @hybrid_property
    def get_parrish(self):
        return self.parrish

    @hybrid_property
    def get_postalCode(self):
        return self.postalCode

    @hybrid_property
    def get_userid(self):
        return self.userid

    
class Cart(db.Model):
    __tablename__ = 'cart'
    dateCreated = db.Column(db.datetime,nullable=False)
    total = db.Column(db.Decimal,nullable=False)
    userid = db.Column(db.Integer,db.ForeignKey('user.userid'),nullable=False)
    cartId = db.Column(db.Integer,nullable=False,primary_key=True)


    def __init__(self,dateCreated,total,userid,cartId):
        self.dateCreated = dateCreated
        self.total = total
        self.userid = userid
        self.cartId = cartId

    def checkAvailability(productId,quantity):
        product = Product.query.filter_by(productId=productId).first()
        if not product:
            response = "Not Available"
        if product:
            if quantity > product.quantity:
                response = "quantity higher than what is available"
            else:
                response =" Product available"
        return response

    def emptyCart(userid):
        pass

    def addToCart(userid,productId,quantity):
        product = Product.query.filter_by(productId=productId).first()
        cart = Cart.query.filter_by(userid = userid).first()
        cartitem = cartItem(cartId = cart.cartId,
            productId = product.productId,
            quantity= quantity)
        db.session.add(cartItem) 
        db.session.commit()

    def removeFromCart(userid,productId):
        pass


    def calculateTotal(userid,productId):
        total = 0
        cart = Cart.query.filter_by(userid = userid).first()
        cartItems = db.session.query(cartItem).filter_by(cartId=cart.cartId).all()
        for item in cartItems:
            product = Product.query.filter_by(productId=item.productId).first()
            total+=item.quantity*product.price
        return total

    def get_dateCreated(self):
        return self.dateCreated

    def get_total(self):
        self.total


    def getItems(userid):
        List = []
        cart = Cart.query.filter_by(userid = userid).first()
        cartItems = db.session.query(cartItem).filter_by(cartId=cart.cartId).all()
        for item in cartItems:
            product = Product.query.filter_by(productId=item.productId).first()
            List.append(product)
        return List

class Product(db.Model):
    __tablename__ = 'product'
    productId = db.Column(db.Integer,primary_key=True,nullable=False)
    name = db.Column(db.String,nullable=False)
    description = db.Column(db.String,nullable=False)
    price = db.Column(db.Decimal,nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    image = db.Column(db.String,nullable=False)

    def __init__(self,productId,name,description,price,quantity,image):
        self.productId = productId
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.image = image

    @hybrid_property
    def get_productId(self):
        return self.productId

    @hybrid_property
    def get_name(self):
        return self.name

    @hybrid_property
    def get_description(self):
        return self.description

    @hybrid_property
    def get_price(self):
        return self.price

    @hybrid_property
    def get_quantity(self):
        return self.quantity

    @hybrid_property
    def get_image(self):
        return self.image 

class cartItem(db.Column):
    __tablename__ = 'cartitem'
    cartId = db.Column(db.Integer,db.ForeignKey(Cart.cartId),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    productId = db.Column(db.Integer,db.ForeignKey(Product.productId),nullable=False)

    def __init__(self,cartId,quantity,productId):
        self.cartId = cartId
        self.quantity = quantity
        self.productId = productId
        

class Order(db.Model):
    __tablename__ = 'order'
    orderId = db.Column(db.Integer,nullable=False,primary_key=True)
    orderDate = db.Column(db.String,nullable=False)
    deliveryDate = db.Column(db.String,nullable=False)
    orderStatus = db.Column(db.String,nullable=False)
    total = db.Column(db.Float,nullable=False)
    userid = db.Column(db.Integer,db.ForeignKey("user.userid"),nullable=False)

    def __init__(self,orderId,orderDate,deliveryDate,orderStatus,total,userid):
        self.orderId = orderId
        self.orderDate = orderDate
        self.deliveryDate = deliveryDate
        self.orderStatus = orderStatus
        self.total = total
        self.userid = userid

    @hybrid_property
    def get_orderId(self):
        return self.orderId

    @hybrid_property
    def get_orderDate(self):
        return self.orderDate

    @hybrid_property
    def get_deliveryDate(self):
        return self.deliveryDate

    @hybrid_property
    def get_orderStatus(self):
        return self.orderStatus

    @hybrid_property
    def get_total(self):
        return self.total

    @hybrid_property
    def get_userid(self):
        return self.userid
        
    

class Order_User(db.Model):
    __tablename__ = 'order_user'
    userid = db.Column(db.Integer,db.ForeignKey(User.userid),nullable=False,)
    orderid = db.Column(db.Integer,db.ForeignKey(Order.orderId),nullable=False)

    def __init__(self,userid,orderid):
        self.userid = userid
        self.orderid = orderid

        