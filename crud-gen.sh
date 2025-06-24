if ! [ -f ".env" ];then
    echo ".env file not found"
    exit 1
fi

if [ -z "$3" ]; then
    echo "Use: $0 <app_name> <view_name> <table_name>"
    exit 1
fi


DIR=./web/src/views/$1/$2


# 设置数据库连接信息
HOST="177.10.0.13"
USER="root"
PASSWORD=$(cat .env | grep MYSQL_PASSWORD |  sed 's/^.*MYSQL_PASSWORD=//g')
DATABASE="django-vue3-admin"
TABLE=$3
TARGET_FILE="./web/src/views/$1/$2/crud.tsx"


# 表是否存在
TABLE_EXISTS=$(mysql -h $HOST -u $USER -p$PASSWORD -D $DATABASE -e "SHOW TABLES LIKE '$TABLE';" -N | grep "$TABLE" | wc -l)

if [ "$TABLE_EXISTS" -eq 0 ]; then
    echo "Table $TABLE does not exist in database $DATABASE."
    exit 1
fi

mkdir -p $DIR
cp -r ./web/src/views/template/* $DIR
sed -i "s/VIEWSETNAME/$2/g" $DIR/*

sed -n -e :a -e '1,5!{P;N;D;};N;ba' -i $TARGET_FILE

# 查询表结构
QUERY="SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT, IS_NULLABLE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '$DATABASE' AND TABLE_NAME = '$TABLE' ORDER BY ORDINAL_POSITION;"

# 使用 MySQL 查询获取字段信息，并生成 fast-crud 配置
mysql -h $HOST -u $USER -p$PASSWORD -D $DATABASE -e "$QUERY" -N | while read COLUMN_NAME DATA_TYPE COLUMN_COMMENT IS_NULLABLE; do
    # 映射 MySQL 数据类型到 fast-crud 类型
    case "$DATA_TYPE" in
        "int"|"bigint"|"smallint"|"mediumint"|"tinyint"|"decimal"|"float"|"double")
            TYPE="number"
            ;;
        "date"|"datetime"|"timestamp")
            TYPE="date"
            ;;
        *)
            TYPE="text"
            ;;
    esac

    echo "                $COLUMN_NAME: {
                    title: '$COLUMN_NAME',
                    type: '$TYPE',
                    search: { show: true },
                    column: {
                        minWidth: 120,
                        sortable: 'custom',
                    },
                    form: {" >> $TARGET_FILE

    if [ "$IS_NULLABLE" = "NO" ]; then
        echo "                        helper: {
                            render() {
                                return <div style={"color:blue"}>$COLUMN_NAME 是必填的</div>;
                            }
                        },
                        rules: [{
                            required: true, message: '$COLUMN_NAME 是必填的'
                        }]," >> $TARGET_FILE
    fi

    echo "                        component: {
                            placeholder: '请输入 $COLUMN_NAME',
                        },
                    },
                }," >> $TARGET_FILE
done

echo "            },
        },
    };
}" >> $TARGET_FILE
