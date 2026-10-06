<template>
  <div class="xiaohongshu-settings-page">
    <div class="page-header">
      <h2 class="page-title">小红书账号管理</h2>
      <p class="page-desc">管理多个小红书账号的登录凭证（a1 + web_session），用于发布时选择对应账号</p>
    </div>

    <div class="form-section">
      <h3 class="form-section-title">{{ editingId ? '编辑账号' : '添加账号' }}</h3>
      <el-form ref="formRef" :model="form" label-position="top" class="config-form">
        <el-form-item label="账号备注名" prop="name" required>
          <el-input
            v-model="form.name"
            placeholder="如：个人号、品牌号等，便于区分"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="a1" prop="a1" required>
          <el-input
            v-model="form.a1"
            placeholder="从小红书浏览器 Cookie 中获取的 a1 值"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="web_session" prop="web_session" required>
          <el-input
            v-model="form.web_session"
            placeholder="从小红书浏览器 Cookie 中获取的 web_session 值"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">{{ editingId ? '保存' : '添加' }}</el-button>
          <el-button v-if="editingId" @click="handleCancelEdit">取消</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="list-section">
      <h3 class="list-section-title">已添加账号（{{ list.length }}）</h3>
      <div v-if="loading" class="list-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中…</span>
      </div>
      <div v-else-if="list.length > 0" class="table-wrap">
        <el-table :data="list" stripe class="config-table">
          <el-table-column prop="name" label="备注名" min-width="120" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="account-name-cell">{{ row.name || '未命名账号' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="a1" min-width="180">
            <template #default="{ row }">
              <span class="cookie-cell">{{ row.a1 ? row.a1.slice(0, 40) + '…' : '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="web_session" min-width="180">
            <template #default="{ row }">
              <span class="cookie-cell">{{ row.web_session ? row.web_session.slice(0, 40) + '…' : '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="添加时间" min-width="160" />
          <el-table-column label="操作" width="140" align="right" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="暂无账号，请在上方添加" class="empty-wrap" />
    </div>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getXhsAccounts, addXhsAccount, updateXhsAccount, deleteXhsAccount } from '@/apis'

export default {
  name: 'XiaohongshuSettings',
  components: { Loading },
  data() {
    return {
      list: [],
      loading: false,
      saving: false,
      editingId: null,
      form: {
        name: '',
        a1: '',
        web_session: '',
      },
    }
  },
  mounted() {
    this.loadList()
  },
  methods: {
    async loadList() {
      this.loading = true
      try {
        const data = await getXhsAccounts()
        this.list = data || []
      } catch {
        this.list = []
        ElMessage.error('加载账号列表失败')
      } finally {
        this.loading = false
      }
    },
    handleSave() {
      const name = (this.form.name || '').trim()
      const a1 = (this.form.a1 || '').trim()
      const webSession = (this.form.web_session || '').trim()
      if (!name) {
        ElMessage.warning('请填写账号备注名')
        return
      }
      if (!a1) {
        ElMessage.warning('请填写 a1')
        return
      }
      if (!webSession) {
        ElMessage.warning('请填写 web_session')
        return
      }

      this.saving = true
      const promise = this.editingId
        ? updateXhsAccount({ account_id: this.editingId, name, a1, web_session: webSession })
        : addXhsAccount({ name, a1, web_session: webSession })

      promise
        .then(() => {
          ElMessage.success(this.editingId ? '已更新' : '已添加')
          this.resetForm()
          this.loadList()
        })
        .catch((err) => {
          const msg = err?.response?.data?.detail || err?.message || '操作失败'
          ElMessage.error(msg)
        })
        .finally(() => {
          this.saving = false
        })
    },
    handleCancelEdit() {
      this.editingId = null
      this.resetForm()
    },
    handleEdit(row) {
      this.editingId = row.id
      this.form.name = row.name || ''
      this.form.a1 = row.a1 || ''
      this.form.web_session = row.web_session || ''
    },
    handleDelete(row) {
      ElMessageBox.confirm(`确定删除「${row.name || '未命名'}」吗？`, '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      })
        .then(async () => {
          try {
            await deleteXhsAccount(row.id)
            if (this.editingId === row.id) {
              this.handleCancelEdit()
            }
            this.loadList()
            ElMessage.success('已删除')
          } catch (err) {
            ElMessage.error(err?.response?.data?.detail || '删除失败')
          }
        })
        .catch(() => {})
    },
    resetForm() {
      this.editingId = null
      this.form.name = ''
      this.form.a1 = ''
      this.form.web_session = ''
    },
  },
}
</script>

<style lang="scss" scoped>
$primary: #FF6B47;
$primary-bg: #fff8f6;
$text: #303133;
$text-secondary: #606266;
$border: #e4e7ed;
$radius: 12px;
$radius-sm: 8px;

.xiaohongshu-settings-page {
  width: 100%;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: $text;
  margin: 0 0 12px;
}

.page-desc {
  font-size: 14px;
  color: $text-secondary;
  margin: 0;
  line-height: 1.5;
}

.form-section {
  margin-bottom: 40px;
  padding: 24px;
  background: $primary-bg;
  border-radius: $radius;
  border: 1px solid $border;
}

.form-section-title {
  font-size: 16px;
  font-weight: 600;
  color: $text;
  margin: 0 0 20px;
}

.config-form {
  max-width: 640px;
}

.list-section-title {
  font-size: 16px;
  font-weight: 600;
  color: $text;
  margin: 0 0 16px;
}

.list-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 24px 0;
  font-size: 14px;
  color: $text-secondary;
  .is-loading { font-size: 20px; }
}

.table-wrap {
  border-radius: $radius;
  overflow: hidden;
  border: 1px solid $border;
}

.account-name-cell {
  font-weight: 500;
  color: $text;
}

.cookie-cell {
  font-size: 13px;
  color: $text-secondary;
  word-break: break-all;
  font-family: monospace;
}

:deep(.config-table) {
  --el-table-border-color: #{$border};
  --el-table-header-bg-color: #f5f7fa;
}
:deep(.config-table .el-table__header th) {
  font-weight: 600;
  color: $text;
}
:deep(.config-table .el-button.is-link) {
  font-weight: 500;
}

.empty-wrap {
  padding: 48px 0;
}
.empty-wrap :deep(.el-empty__description) {
  color: $text-secondary;
}
</style>
