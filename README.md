# 概要
slack通知用のサンプル

# 使い方
## 開発手順
mainブランチから、都度開発用のfeatureブランチを作成し開発し、プルリクエストにてmainブランチにマージする運用とする。
プルリクエスト作成/更新時は、テスト用のLambda関数にデプロイおよびローカルでのテスト(slackへは通知せずlogsに出力する)を実施する。
プルリクエストのマージ時は、本番用のLambda関数に新しいコードがデプロイされる。
### 開発用branchの作成とコードの開発
ローカルにリポジトリをcloneしfeatureブランチを作成する。
```sh
git clone <該当リポジトリのパス>
cd <リポジトリ名>
git branch --contains
<mainブランであることを確認する>
```
コード追加/修正のための新しいブランチをmainブランチから作成する。
```sh
git ckeckout -b "任意のブランチ名称"
```
コードの追加修正が完了したら、コミットしリモートにpushします。(git操作の詳細は割愛します)

### mainブランチへのマージ
pull reqとapprovalにより、mainブランチにマージします。


## slack SDKの更新方法
```sh
pip install --target .  --upgrade slack_sdk
```

# ディレクトリ構成


