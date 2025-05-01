-- Schema for TurboExress.AI

CREATE TABLE public.users
(
    user_id character varying(20) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    location character varying(100),
    password character varying(100),
    PRIMARY KEY (user_id)
);

CREATE TABLE public.agent
(
    agent_id character varying(20) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    password character varying(100),
    PRIMARY KEY (agent_id)
);

CREATE TABLE public.L1Catg
(
    l1_catg character varying(20) NOT NULL,
    prio int,
    PRIMARY KEY (l1_catg)
);

CREATE TABLE public.L2Catg
(
    l1_catg character varying(20) NOT NULL,
    l2_catg character varying(50) NOT NULL,
    prio int,
    FOREIGN KEY (l1_catg)  REFERENCES public.L1Catg(l1_catg),
    PRIMARY KEY (l2_catg)
);

CREATE TABLE public.L3Catg
(
    l1_catg character varying(20) NOT NULL,
    l2_catg character varying(50) NOT NULL,
    l3_catg character varying(50) NOT NULL,
    prio int,
    FOREIGN KEY (l2_catg)  REFERENCES public.L2Catg(l2_catg),
    PRIMARY KEY (l3_catg)
);

CREATE TABLE public.product
(
    product_id int NOT NULL, 
    l1_catg character varying(20) NOT NULL,
    l2_catg character varying(50) NOT NULL,
    l3_catg character varying(50) NOT NULL,
    product_name character varying(100) NOT NULL,
    price FLOAT, 
    product_desc character varying(1000) NOT NULL,
    image_url character varying(500) NOT NULL,
    gender character varying(10) NOT NULL,
    brand character varying(50) NOT NULL,
    rating decimal,
    FOREIGN KEY (l3_catg) REFERENCES public.L3Catg(l3_catg),
    PRIMARY KEY (product_id)
);

CREATE TABLE public.stock
(
    product_id int NOT NULL, 
    quantity int DEFAULT 0,
    PRIMARY KEY (product_id)
);


CREATE TABLE public.forecast
(
    product_id int NOT NULL, 
    quantity int DEFAULT 0,
    PRIMARY KEY (product_id)
);

CREATE TABLE public.cart
(
    user_id character varying(20) NOT NULL,
    delv_message character varying(500) NOT NULL,
    date date DEFAULT CURRENT_DATE NOT NULL,     
    status character varying(50) NOT NULL,
    prio int,
    FOREIGN KEY (user_id)  REFERENCES public.users(user_id),
    PRIMARY KEY (user_id)
);



CREATE TABLE public.cartItem
(
    user_id character varying(20) NOT NULL,
    cartitem_id int NOT NULL,
    product_id int NOT NULL, 
    quantity int DEFAULT 0, 
    price FLOAT, 
    FOREIGN KEY (user_id)  REFERENCES public.users(user_id)
);


CREATE TABLE public.order 
(
    order_id int NOT NULL,     
    user_id character varying(20) NOT NULL,
    delv_message character varying(500) NOT NULL,   
    status character varying(50) NOT NULL,  
    order_date date DEFAULT CURRENT_DATE NOT NULL,     
    accepted_date date,
    pick_date date,     
    delivery_date date,   
    agent_id character varying(20) NOT NULL,
	PRIMARY KEY (order_id)
);

CREATE TABLE public.orderitem
(
    order_id int NOT NULL,
    orderitem_id int NOT NULL,
    product_id int NOT NULL, 
    quantity int DEFAULT 0, 
    price FLOAT, 
    FOREIGN KEY (order_id)  REFERENCES public.order(order_id)
);

CREATE TABLE public.eventcongif
(
    date date DEFAULT CURRENT_DATE NOT NULL,
    event_name character varying(50) NOT NULL,
    demand_type character varying(10) NOT NULL,
    l2_catg character varying(50) NOT NULL,
    product_name character varying(100) NOT NULL,
    FOREIGN KEY (l2_catg) REFERENCES public.l2catg(l2_catg)
);


CREATE TABLE public.weathercongif
(
    weather_name character varying(50) NOT NULL,
    demand_type character varying(10) NOT NULL,
    l2_catg character varying(50) NOT NULL,
    product_name character varying(100) NOT NULL,
    FOREIGN KEY (l2_catg) REFERENCES public.l2catg(l2_catg)
);

