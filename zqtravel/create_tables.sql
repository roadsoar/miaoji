/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     1/4/2015 5:35:29 AM                          */
/*==============================================================*/


create database zqtravel;
use zqtravel;

drop table if exists Airtickets;

drop table if exists AttributeClass;

drop table if exists City;

drop table if exists Continent;

drop table if exists Country;

drop table if exists Hotelinfo;

drop table if exists Province;

drop table if exists Scenicspot;

drop table if exists Tag;

drop table if exists Travelnotes;

/*==============================================================*/
/* Table: Airtickets                                            */
/*==============================================================*/
create table Airtickets
(
   flight_no            varchar(100),
   airlines             varchar(100),
   departure_time       time,
   arrival_time         time,
   origin               varchar(100),
   destination          varchar(100),
   info_url             varchar(100),
   punctuality          varchar(50),
   price                float
);

/*==============================================================*/
/* Table: AttributeClass                                        */
/*==============================================================*/
create table AttributeClass
(
   AttributeClass_no    numeric(20,0) not null,
   AttributeClass_name  varchar(100),
   primary key (AttributeClass_no)
);

alter table AttributeClass comment '属性类别';

/*==============================================================*/
/* Table: Continent                                             */
/*==============================================================*/
create table Continent
(
   Continent_no         numeric(20,0) not null,
   Continent_name       varchar(100),
   Continent_intrd      varchar(10000),
   primary key (Continent_no)
);

alter table Continent comment '大洲';

/*==============================================================*/
/* Table: Country                                               */
/*==============================================================*/
create table Country
(
   Country_no           numeric(20,0) not null,
   Country_name         varchar(100),
   Country_intrd        varchar(10000),
   Continent_no         numeric(20,0),
   primary key (Country_no)
);

alter table Country comment '国家';

/*==============================================================*/
/* Table: Hotelinfo                                             */
/*==============================================================*/
create table Hotelinfo
(
   hotel_no             numeric(20,0) not null,
   hotel_name           varchar(100),
   city_no              numeric(20,0),
   star_level           int,
   type                 int,
   info_url             varchar(100),
   lowest_price         float,
   highest_price        float,
   primary key (hotel_no)
);

/*==============================================================*/
/* Table: Tag                                                   */
/*==============================================================*/
create table Tag
(
   Tag_no               numeric(20,0) not null,
   Tag_name             varchar(100),
   AttributeClass_no    numeric(20,0),
   primary key (Tag_no)
);

alter table Tag comment '标签';

/*==============================================================*/
/* Table: Travelnotes                                           */
/*==============================================================*/
create table Travelnotes
(
   Travelnotes_no       numeric(20,0) not null,
   Travelnotes_title    varchar(1000),
   Travelnotes_url      varchar(100),
   Travelnotes_intrd    varchar(80000),
   Travelnotes_commentnum int,
   Scenicspot_no        numeric(20,0),
   Travelnotes_time     date,
   Travelnotes_from     varchar(100),
   primary key (Travelnotes_no)
);

alter table Travelnotes comment '游记';

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


alter table Country add constraint FK_Reference_2 foreign key (Continent_no)
      references Continent (Continent_no) on delete restrict on update restrict;

alter table Province add constraint FK_Reference_3 foreign key (Country_no)
      references Country (Country_no) on delete restrict on update restrict;

alter table City add constraint FK_Reference_1 foreign key (Province_no)
      references Province (Province_no) on delete restrict on update restrict;

alter table Scenicspot add constraint FK_Reference_4 foreign key (City_no)
      references City (City_no) on delete restrict on update restrict;

alter table Tag add constraint FK_Reference_6 foreign key (AttributeClass_no)
      references AttributeClass (AttributeClass_no) on delete restrict on update restrict;

alter table Travelnotes add constraint FK_Reference_5 foreign key (Scenicspot_no)
      references Scenicspot (Scenicspot_no) on delete restrict on update restrict;


insert into Continent values(1,'亚洲','亚洲');
insert into Continent values(2,'欧洲','欧洲');
insert into Country values(100,'中国','中华民族伟大复兴，梦醒！',1);

