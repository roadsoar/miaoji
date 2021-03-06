﻿drop table if exists Scenicspot;

drop table if exists City;

drop table if exists Province;

/*==============================================================*/
/* Table: City                                                  */
/*==============================================================*/
create table City
(
   City_no              numeric(20,0) not null,
   City_name            varchar(100),
   City_intrd           text,
   City_best_traveling_time text,
   City_dressing varchar(500),
   City_custom          text,
   City_culture         text,
   City_history         text,
   City_weather         varchar(500),
   City_days            varchar(100),
   City_area            float,
   City_language        text,
   Province_no          numeric(20,0),
   primary key (City_no)
);

alter table City comment '城市';


/*==============================================================*/
/* Table: Province                                              */
/*==============================================================*/
create table Province
(
   Province_no          numeric(20,0) not null,
   Province_name        varchar(100),
   Province_intrd       text,
   Province_traveling_time   text,
   Province_dressing    varchar(500),
   Province_custom    text,
   Province_culture    text,
   Province_history    text,
   Province_weather    varchar(500),
   Province_days    varchar(100),
   Province_language        text,
   Country_no           numeric(20,0),
   primary key (Province_no)
);

alter table Province comment '省';

/*==============================================================*/
/* Table: Scenicspot                                            */
/*==============================================================*/
create table Scenicspot
(
   Scenicspot_no        numeric(20,0) not null,
   Scenicspot_name      varchar(600),
   Scenicspot_en        varchar(1000),
   Scenicspot_level     float,
   Scenicspot_heat      int,
   City_no              numeric(20,0),
   Scenicspot_intrd     text,
   Scenicspot_address   varchar(500),
   Scenicspot_telephone     varchar(100),
   Scenicspot_web       varchar(100),
   Scenicspot_moftrans  varchar(100),
   Scenicspot_ticketprice varchar(1000),
   Scenicspot_opentime   varchar(2000),
   Scenicspot_usetime   varchar(2000),
   Scenicspot_comments  text,
   Scenicspot_impression   varchar(200),
   Scenicspot_traffic   varchar(1000),
   primary key (Scenicspot_no)
);

alter table Scenicspot comment '景区';


alter table Province add constraint FK_Reference_3 foreign key (Country_no)
      references Country (Country_no) on delete restrict on update restrict;

alter table City add constraint FK_Reference_1 foreign key (Province_no)
      references Province (Province_no) on delete restrict on update restrict;

alter table Scenicspot add constraint FK_Reference_4 foreign key (City_no)
      references City (City_no) on delete restrict on update restrict;

