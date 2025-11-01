# Claude Code 補強プロンプト - マルチインスタンス協調システム追加

## 🔄 既存システムへの追加統合プロンプト

### 1. マルチインスタンス並列ワークフロー追加

```
現在の自律開発システムに、Anthropicエンジニアが推奨する「複数Claude Code並列実行」機能を追加してください。

追加実装内容：
1. **Git Worktree並列実行の強化**
   - 各worktreeに独立したClaude Codeインスタンスを割り当て
   - 並列で複数のgit checkoutを実行
   - SSH + TMUX環境での並列セッション管理

2. **インスタンス間の情報共有メカニズム**
   - GitHub Issuesを通じた進捗共有
   - テキストファイルベースの状態同期
   - メール/Slackを使った通知連携

3. **GitHub Actions並列起動**
   - 各worktreeごとに独立したActionワークフロー
   - 並列実行の調整と結果集約

実装場所：
- src/parallel_execution/multi_instance_manager.py
- .github/workflows/parallel-claude-execution.yml
- config/parallel_execution.yaml

既存のWorktreeManagerとEvaluationSystemを拡張して実装してください。
```

### 2. Project Memory システムの実装

```
新しくチームに参加したメンバー（Claude Codeインスタンス）向けに、Project Memoryシステムを実装してください。

実装内容：
1. **オンボーディングドキュメント自動生成**
   - プロジェクト概要
   - 技術スタック説明
   - 開発規約とパターン
   - 既存実装の解説

2. **コンテキスト管理システム**
   - docs/PROJECT_CONTEXT.md の自動更新
   - 重要な意思決定の記録
   - 失敗と学習の蓄積

3. **知識共有プロトコル**
   - 新規Claude Codeインスタンス起動時の自動ブリーフィング
   - GitHub Issues/Jira/テキストファイルでの情報永続化
   - 実装パターンのテンプレート化

実装ファイル：
- src/memory/project_memory.py
- docs/PROJECT_CONTEXT.md
- scripts/onboarding_claude.sh

既存のシステムを中断せずに追加実装してください。
```

### 3. テックリード型管理システム

```
あなたを「テックリード」として、Claude Codeを「同僚エンジニア」として扱う管理システムを追加してください。

実装内容：
1. **タスク計画と割り当て**
   - まずPLANを作成してからコード実装
   - タスクの優先順位付けと割り当て
   - 各Claude Codeインスタンスへの明確な指示

2. **レビューとフィードバック**
   - 実装結果の自動レビュー
   - 改善点のフィードバックループ
   - ベストプラクティスの抽出と共有

3. **進捗管理ダッシュボード**
   - 各インスタンスの作業状況可視化
   - ボトルネックの検出
   - リソース配分の最適化

追加ファイル：
- src/management/tech_lead_system.py
- src/management/task_planner.py
- dashboard/progress_monitor.html
```

### 4. 強化版GitHub Actions統合

```
CI/CDパイプラインを強化して、複数Claude Codeの並列実行を最適化してください。

追加機能：
1. **並列ワークフロー制御**
   ```yaml
   jobs:
     parallel-claude-execution:
       strategy:
         matrix:
           instance: [1, 2, 3, 4, 5]
       steps:
         - name: Claude Code Instance ${{ matrix.instance }}
           run: |
             # 独立したworktreeで実行
             git worktree add ../claude-${{ matrix.instance }}
             cd ../claude-${{ matrix.instance }}
             claude-code execute --instance-id ${{ matrix.instance }}
```

1. **インスタンス間調整**
- 実行順序の動的調整
- リソース競合の回避
- 結果の自動マージ
1. **失敗時の自動リトライ**
- 別インスタンスでの再実行
- エラーパターンの学習
- 自動回復メカニズム

更新対象：

- .github/workflows/autonomous-development.yml
- scripts/parallel_coordinator.py

```
### 5. 通知とモニタリング強化
```

Claude Coreからの通知を活用した、リアルタイムモニタリングシステムを追加してください。

実装内容：

1. **通知ハブの構築**
- Claude Core通知の自動処理
- 重要イベントの抽出とアラート
- 進捗の可視化
1. **文字起こし機能の活用**
- 実行ログの自動テキスト化
- 重要な決定の記録
- ナレッジベースの自動構築
1. **インテリジェント通知**
- 異常検知時の即座アラート
- 成功パターンの通知
- 改善提案の自動生成

追加コンポーネント：

- src/monitoring/notification_hub.py
- src/monitoring/transcription_processor.py
- config/alerting_rules.yaml

```
### 6. ドキュメント自動更新システム
```

Anthropicエンジニアが最も重要視する「ドキュメント更新」を自動化してください。

実装内容：

1. **自動ドキュメント生成**
- コード変更の自動文書化
- API仕様の自動更新
- アーキテクチャ図の自動生成
1. **テンプレート駆動更新**
- README.mdの自動更新
- CHANGELOG.mdの自動生成
- 技術決定記録（ADR）の作成
1. **知識の永続化**
- 実装パターンのカタログ化
- トラブルシューティングガイド
- ベストプラクティス集

実装：

- src/documentation/auto_documenter.py
- templates/documentation/
- scripts/update_docs.sh

```
## 🚀 段階的統合プロンプト

### Phase 1: 基盤追加（既存システムを停止せずに実行）
```

現在稼働中のシステムに影響を与えずに、以下を追加してください：

1. parallel_execution/ディレクトリを作成
1. マルチインスタンス管理クラスを実装
1. 既存のWorktreeManagerを拡張（継承して新クラス作成）
1. テスト環境で並列実行を検証

既存の自律開発は継続しながら、新機能を段階的に統合してください。

```
### Phase 2: 協調メカニズム追加
```

複数Claude Codeインスタンス間の協調を実現してください：

1. GitHub Issuesをメッセージバスとして活用
- 各インスタンスが進捗をIssueコメントに投稿
- タスクの認領と完了通知
1. 共有ナレッジベースの構築
- docs/shared_knowledge/に蓄積
- 成功/失敗パターンの記録
1. インスタンス間の自動調整
- 重複作業の検出と回避
- リソースの動的再配分

```
### Phase 3: 完全統合と最適化
```

新旧システムを完全統合して、最適化してください：

1. 既存の5つの開発パターンと並列実行の統合
1. 評価システムの拡張（並列実行結果の評価）
1. セキュリティポリシーの適用確認
1. パフォーマンスベンチマーク実行

統合後のシステムが、単一実行時より10倍の開発速度を達成することを確認してください。

```
## 💡 実行時の注意事項

### 既存システムとの互換性維持
```

追加実装時は必ず：

1. 既存のAPIとインターフェースを保持
1. 後方互換性を確保
1. 段階的な移行パスを提供
1. ロールバック可能な実装

```
### モニタリング強化
```

新機能追加後は：

1. 並列実行のリソース使用状況を監視
1. インスタンス間の通信遅延を測定
1. 全体的なスループットを追跡
1. エラー率の変化を記録

```
## 📋 検証チェックリスト

追加実装の完了基準：
- [ ] 5つ以上のClaude Codeが並列実行可能
- [ ] GitHub Issues経由での情報共有が機能
- [ ] Project Memoryが新インスタンスに自動共有
- [ ] ドキュメントが自動更新される
- [ ] 既存システムとの完全互換性
- [ ] セキュリティ要件を満たす
- [ ] パフォーマンスが10倍向上

このプロンプトを既存のシステムに追加することで、Anthropicエンジニアの知見を活かした強化が可能になります。
```