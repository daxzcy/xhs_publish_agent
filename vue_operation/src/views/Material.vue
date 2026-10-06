<template>
  <div class="material-page">
    <div class="page-header">
      <h2 class="page-title">素材库</h2>
      <p class="page-desc">管理图片、文案等素材，便于创作时复用</p>
      <div class="toolbar">
        <el-radio-group v-model="activeTab" class="tab-group">
          <el-radio-button label="image">图片</el-radio-button>
          <el-radio-button label="copy">文案</el-radio-button>
        </el-radio-group>
        <template v-if="activeTab === 'image'">
          <el-upload
            class="upload-inline"
            :show-file-list="false"
            accept="image/jpeg,image/png,image/gif,image/webp"
            :before-upload="beforeUpload"
            :http-request="handleUploadRequest"
          >
            <el-button type="primary" class="upload-btn" :loading="uploading">
              <el-icon><Upload /></el-icon>
              上传素材
            </el-button>
          </el-upload>
          <el-button type="primary" plain class="url-upload-btn" @click="showUrlUploadDialog">
            <el-icon><Link /></el-icon>
            网络图片
          </el-button>
        </template>
        <template v-if="activeTab === 'copy'">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索标题或内容..."
            clearable
            class="search-input"
            prefix-icon="Search"
          />
          <el-button type="primary" class="add-copy-btn" @click="openCopyDialog()">
            <el-icon><Plus /></el-icon>
            新增文案
          </el-button>
        </template>
      </div>
    </div>

    <div v-if="activeTab === 'image'" class="content-wrap">
      <div v-if="imageList.length > 0" class="image-grid">
        <div
          v-for="item in imageList"
          :key="item.id"
          class="image-item"
          @click="handlePreview(item)"
        >
          <div class="image-thumb">
            <img :src="item.url" :alt="item.name" />
          </div>
          <div class="image-overlay" @click.stop>
            <el-button type="primary" size="small" @click="handleUseImage(item)">使用</el-button>
            <el-button type="danger" size="small" @click="handleDeleteImage(item.id)">删除</el-button>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无图片素材" class="empty-wrap">
        <el-upload
          :show-file-list="false"
          accept="image/jpeg,image/png,image/gif,image/webp"
          :before-upload="beforeUpload"
          :http-request="handleUploadRequest"
        >
          <el-button type="primary" :loading="uploading">上传图片</el-button>
        </el-upload>
      </el-empty>
    </div>

    <el-dialog
      v-model="previewVisible"
      title="预览"
      width="80%"
      max-width="800px"
      align-center
      append-to-body
      @close="previewUrl = ''"
    >
      <img v-if="previewUrl" :src="previewUrl" class="preview-img" alt="预览" />
    </el-dialog>

    <!-- 网络 URL 上传对话框 -->
    <el-dialog
      v-model="urlUploadDialogVisible"
      title="通过网络 URL 添加素材图片"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item label="图片 URL">
          <el-input
            v-model="urlUploadInput"
            placeholder="请输入网络图片 URL，如 https://example.com/image.jpg"
            clearable
          />
        </el-form-item>
        <el-form-item v-if="urlUploadInput" label="预览">
          <img
            :src="urlUploadInput"
            class="url-upload-preview"
            @error="urlPreviewError = true"
            v-show="!urlPreviewError"
          />
          <span v-show="urlPreviewError" class="url-preview-error">图片加载失败</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="urlUploadDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="urlUploading"
          :disabled="!urlUploadInput.trim()"
          @click="handleUrlUpload"
        >
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 文案列表 -->
    <div v-if="activeTab === 'copy'" class="content-wrap">
      <div v-if="filteredCopyList.length > 0" class="copy-list">
        <div
          v-for="item in filteredCopyList"
          :key="item.id"
          class="copy-item"
        >
          <div v-if="item.title" class="copy-title">{{ item.title }}</div>
          <div class="copy-content">{{ item.content }}</div>
          <div class="copy-meta">
            <span class="copy-time">{{ item.createTime }}</span>
            <div class="copy-actions">
              <el-button type="primary" link size="small" @click="handleUseCopy(item)">使用</el-button>
              <el-button type="primary" link size="small" @click="openCopyDialog(item)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteCopy(item.id)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else :description="searchKeyword ? '没有匹配的文案' : '暂无文案素材'" class="empty-wrap">
        <el-button type="primary" @click="openCopyDialog()">新增文案</el-button>
      </el-empty>
    </div>

    <!-- 新增/编辑文案对话框 -->
    <el-dialog
      v-model="copyDialogVisible"
      :title="editingCopyId ? '编辑文案' : '新增文案'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form label-width="60px">
        <el-form-item label="标题">
          <el-input v-model="copyForm.title" placeholder="给文案起个标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="copyForm.content"
            type="textarea"
            :rows="8"
            placeholder="输入文案内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="copySaving" @click="handleSaveCopy">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { Upload, Link, Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCookie } from '@/utils/cookie'
import {
  getMaterialImages, uploadMaterialImage, deleteMaterialImage,
  getMaterialCopies, uploadMaterialImageByUrl,
  createMaterialText, updateMaterialText, deleteMaterialText, useMaterialText, uploadTitleImageByUrl,
} from '@/apis'

export default {
  name: 'Material',
  components: { Upload, Link, Plus, Search },
  data() {
    return {
      activeTab: 'image',
      imageList: [],
      copyList: [],
      searchKeyword: '',
      uploading: false,
      previewVisible: false,
      previewUrl: '',
      urlUploadDialogVisible: false,
      urlUploadInput: '',
      urlUploading: false,
      urlPreviewError: false,
      copyDialogVisible: false,
      copySaving: false,
      editingCopyId: null,
      copyForm: { title: '', content: '' },
    }
  },
  computed: {
    filteredCopyList() {
      const kw = (this.searchKeyword || '').trim().toLowerCase()
      if (!kw) return this.copyList
      return this.copyList.filter(item =>
        (item.title || '').toLowerCase().includes(kw) ||
        (item.content || '').toLowerCase().includes(kw)
      )
    },
  },
  watch: {
    activeTab() {
      if (this.activeTab === 'image') this.loadImages()
      else this.loadCopy()
    },
  },
  mounted() {
    this.loadImages()
    this.loadCopy()
  },
  methods: {
    async loadImages() {
      try {
        const userId = getCookie('userId')
        const res = await getMaterialImages(userId ? { user_id: userId } : {})
        const list = res?.list ?? res?.data?.list ?? []
        this.imageList = (list || []).map((row) => ({
          id: row.id,
          name: this._imageNameFromUrl(row.image_url),
          url: row.image_url,
          createTime: row.created_at || '',
        }))
      } catch (e) {
        ElMessage.error(e?.response?.data?.message || e?.message || '加载图片列表失败')
        this.imageList = []
      }
    },
    _imageNameFromUrl(url) {
      if (!url) return '素材图片'
      try {
        const name = url.split('/').pop() || url
        return name.length > 20 ? name.slice(0, 20) + '…' : name
      } catch {
        return '素材图片'
      }
    },
    beforeUpload(file) {
      const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isImage) { ElMessage.error('仅支持 jpg/png/gif/webp'); return false }
      if (!isLt10M) { ElMessage.error('图片大小不超过 10MB'); return false }
      return true
    },
    async handleUploadRequest({ file }) {
      this.uploading = true
      try {
        const formData = new FormData()
        formData.append('file', file)
        const res = await uploadMaterialImage(formData)
        if (res?.image_url) { ElMessage.success('上传成功'); await this.loadImages() }
        else ElMessage.error('上传失败')
      } catch (e) {
        ElMessage.error(e?.response?.data?.message || e?.message || '上传失败')
      } finally { this.uploading = false }
    },
    handlePreview(item) { this.previewUrl = item.url; this.previewVisible = true },
    async handleUseImage(item) {
      const titleId = sessionStorage.getItem('currentTitleId')
      if (!titleId) {
        ElMessage.warning('请先在创作中心选择一个标题，再回来选图')
        return
      }
      try {
        ElMessage.info('正在添加图片...')
        await uploadTitleImageByUrl({
          title_id: Number(titleId),
          image_url: item.url,
          image_type: 0,
        })
        ElMessage.success('图片已添加到当前笔记')
        this.$router.push('/create')
      } catch (e) {
        ElMessage.error(e?.response?.data?.message || '图片添加失败')
      }
    },
    handleDeleteImage(id) {
      ElMessageBox.confirm('确定删除该图片吗？', '删除确认', {
        confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
      }).then(async () => {
        try { await deleteMaterialImage(id); ElMessage.success('已删除'); await this.loadImages() }
        catch (e) { ElMessage.error(e?.response?.data?.message || '删除失败') }
      }).catch(() => {})
    },
    showUrlUploadDialog() { this.urlUploadInput = ''; this.urlPreviewError = false; this.urlUploadDialogVisible = true },
    async handleUrlUpload() {
      const url = (this.urlUploadInput || '').trim()
      if (!url) { ElMessage.warning('请输入图片 URL'); return }
      if (!/^https?:\/\/.+/i.test(url)) { ElMessage.warning('请输入有效的 HTTP/HTTPS URL'); return }
      this.urlUploading = true
      try {
        const res = await uploadMaterialImageByUrl({ image_url: url })
        if (res?.image_url) { ElMessage.success('上传成功'); this.urlUploadDialogVisible = false; await this.loadImages() }
        else ElMessage.error('上传失败')
      } catch (e) {
        ElMessage.error(e?.response?.data?.message || e?.message || '上传失败')
      } finally { this.urlUploading = false }
    },
    handleDelete(imageId) {
      ElMessageBox.confirm('确定删除该图片吗？', '删除确认', {
        confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
      }).then(async () => {
        try { await deleteMaterialImage(imageId); ElMessage.success('已删除'); await this.loadImages() }
        catch (e) { ElMessage.error(e?.response?.data?.message || e?.message || '删除失败') }
      }).catch(() => {})
    },
    async loadCopy() {
      try {
        const res = await getMaterialCopies()
        const list = res?.list ?? res?.data?.list ?? []
        this.copyList = (list || []).map((row) => ({
          id: row.id,
          title: row.title || '',
          content: row.content || '',
          createTime: row.created_at || '',
        }))
      } catch (e) {
        ElMessage.error(e?.response?.data?.message || e?.message || '加载文案列表失败')
        this.copyList = []
      }
    },
    openCopyDialog(item) {
      if (item) {
        this.editingCopyId = item.id
        this.copyForm.title = item.title
        this.copyForm.content = item.content
      } else {
        this.editingCopyId = null
        this.copyForm.title = ''
        this.copyForm.content = ''
      }
      this.copyDialogVisible = true
    },
    async handleSaveCopy() {
      if (!this.copyForm.content.trim()) { ElMessage.warning('内容不能为空'); return }
      this.copySaving = true
      try {
        const data = { title: this.copyForm.title, content: this.copyForm.content }
        if (this.editingCopyId) {
          await updateMaterialText(this.editingCopyId, data)
          ElMessage.success('修改成功')
        } else {
          await createMaterialText(data)
          ElMessage.success('新增成功')
        }
        this.copyDialogVisible = false
        await this.loadCopy()
      } catch (e) {
        ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
      } finally { this.copySaving = false }
    },
    handleDeleteCopy(id) {
      ElMessageBox.confirm('确定删除这条文案吗？', '删除确认', {
        confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
      }).then(async () => {
        try { await deleteMaterialText(id); ElMessage.success('已删除'); await this.loadCopy() }
        catch (e) { ElMessage.error(e?.response?.data?.message || e?.message || '删除失败') }
      }).catch(() => {})
    },
    async handleUseCopy(item) {
      try {
        const res = await useMaterialText(item.id)
        const titleId = res?.title_id
        sessionStorage.setItem('createCopy', item.content || '')
        sessionStorage.setItem('createCopyTitle', item.title || '素材库复用')
        if (titleId) sessionStorage.setItem('createCopyTitleId', String(titleId))
        this.$router.push('/create')
      } catch (e) {
        ElMessage.error(e?.response?.data?.message || '使用失败')
      }
    },
  },
}
</script>

<style lang="scss" scoped>
$primary: #FF6B47;
$primary-light: #FF8A65;
$primary-bg: #fff8f6;
$text: #303133;
$text-secondary: #606266;
$border: #e4e7ed;
$radius: 12px;
$radius-sm: 8px;

.material-page { width: 100%; }
.page-header { margin-bottom: 32px; }
.page-title { font-size: 24px; font-weight: 600; color: $text; margin: 0 0 12px; }
.page-desc { font-size: 14px; color: $text-secondary; margin: 0 0 24px; line-height: 1.5; }
.toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
.tab-group {
  :deep(.el-radio-button__inner) { border-radius: $radius-sm; }
  :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background: $primary; border-color: $primary; box-shadow: -1px 0 0 0 $primary;
  }
}
.upload-inline { display: inline-block; }
.upload-btn { border-radius: $radius-sm; }
.url-upload-btn { margin-left: 12px; border-radius: $radius-sm; }
.search-input { width: 220px; }
.add-copy-btn { margin-left: 12px; border-radius: $radius-sm; }
.url-upload-preview { max-width: 100%; max-height: 200px; border-radius: 4px; object-fit: contain; }
.url-preview-error { color: #f56c6c; font-size: 13px; }
.content-wrap { min-height: 400px; }
.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 24px; }
.image-item {
  border-radius: $radius; overflow: hidden; border: 1px solid $border; background: #fff;
  cursor: pointer; transition: all 0.3s ease;
  &:hover { border-color: $primary-light; box-shadow: 0 8px 24px rgba(255,107,71,0.12); transform: translateY(-2px); }
}
.image-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  display: flex; gap: 8px; justify-content: center; padding: 8px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  opacity: 0; transition: opacity 0.2s;
}
.image-item { position: relative; }
.image-item:hover .image-overlay { opacity: 1; }
.image-thumb { aspect-ratio: 4/3; overflow: hidden; background: #f5f7fa;
  img { width: 100%; height: 100%; object-fit: cover; display: block; }
}
.copy-list { display: flex; flex-direction: column; gap: 16px; }
.copy-item {
  padding: 20px 24px; border-radius: $radius; border: 1px solid $border;
  background: #fdfdfd; transition: all 0.3s ease;
  &:hover { border-color: $primary-light; box-shadow: 0 4px 16px rgba(255,107,71,0.08); }
}
.copy-title {
  font-size: 13px; color: $primary; font-weight: 600; margin-bottom: 8px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.copy-content {
  font-size: 15px; color: $text; line-height: 1.6; margin-bottom: 12px;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.copy-meta { display: flex; align-items: center; justify-content: space-between; }
.copy-time { font-size: 13px; color: $text-secondary; }
.copy-actions { display: flex; gap: 8px; }
:deep(.copy-actions .el-button.is-link) { color: $primary; }
.preview-img { width: 100%; display: block; border-radius: $radius-sm; }
.empty-wrap { padding: 64px 0; }
.empty-wrap :deep(.el-empty__description) { color: $text-secondary; }
</style>
