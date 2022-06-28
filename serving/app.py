import sys
sys.path.insert(0, sys.path[0] + '/../')
from commons import request, content_wash, softmax
from flask import Flask, request, jsonify
import logging
from conf.params import parse_args
from model.predict import prepare_model, predict


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 保证返回的json编码正确


@app.route('/nlp/emotion/analysis', methods=['POST'])
def generate_summary():
    try:
        packages = request.get_packages()  # 素材包信息
        articles = []
        for pac in packages:
            pac_article = request.get_package_article(package_id=pac.get('packageInfo').get('id'))
            articles.append(pac_article)  # 素材包中已有的文章
        candidates = request.get_package_article()  # 备选的素材池文章
        filter_candidates = [content_wash.filter_tags(cand['content']) for cand in candidates]

        data = request.get_json()
        content = data.get('content')
        app.logger.info('成功接收content: ' + content)
        if len(content) < 1:
            return jsonify(status=112001, msg='content too short')

        result = {"content": content}  # "content": content

        # 预测标签
        output, label_pre = predict(net, device, content)
        app.logger.info('预测完成！！   label: ' + str(label_pre) + ' raw scores: ' + str(output))

        output = softmax.softmax_round2(output)
        app.logger.info('softmax scores: ' + str(output))
        label_pre = 'Negative' if label_pre else 'Positive'
        app.logger.info('process label: ' + label_pre)

        result['label'] = label_pre
        result['score'] = float(max(output))

        app.logger.info('数据封装成功')

        return jsonify(status=200, data=result, msg="success")

    except Exception as e:
        app.logger.info(e)
        return jsonify(status=112001, msg='fail')


# 执行
if __name__ == "__main__":
    args = parse_args()
    net, device = prepare_model()
    handler = logging.FileHandler(args.predict_log)
    app.logger.addHandler(handler)
    app.run(
        host='0.0.0.0',
        port=5063
    )
