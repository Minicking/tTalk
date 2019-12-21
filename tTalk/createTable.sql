create table if not exists user(
	user_id int unsigned auto_increment primary key,
	user_name varchar(20) not null default '新人',
	user_account varchar(20) not null unique,
	user_password varchar(100) not null,
	user_regDate datetime not null,
	user_lastDate datetime not null,
	user_messageCount int unsigned default 0,
	user_lastIP varchar(25) default '0.0.0.0:0000',
	user_messageStyle int unsigned default 0
)engine=innodb default charset=utf8;
create table if not exists chatrecord(
	cr_id int unsigned auto_increment primary key,
	cr_text varchar(100),
	cr_Date datetime not null,
	user_id int unsigned not null,
	foreign key(user_id) references User(user_id)
)engine=innodb default charset=utf8;