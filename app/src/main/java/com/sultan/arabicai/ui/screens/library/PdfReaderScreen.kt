package com.sultan.arabicai.ui.screens.library

import android.content.Context
import android.graphics.Bitmap
import android.graphics.pdf.PdfRenderer
import android.os.ParcelFileDescriptor
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.BookmarkBorder
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.EditNote
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.ui.theme.SultanColors
import java.io.File
import java.io.FileOutputStream
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Real PDF rendering via the platform [PdfRenderer] — no third-party PDF library required.
 * Assets can't be opened by [PdfRenderer] directly (it needs a real file descriptor), so the
 * bundled book is copied into the app's cache directory once on first open.
 */
@Composable
fun PdfReaderScreen(bookId: Long) {
    val container = LocalAppContainer.current
    val context = LocalContext.current

    var book by remember { mutableStateOf<com.sultan.arabicai.data.local.entity.BookEntity?>(null) }
    var renderer by remember { mutableStateOf<PdfRenderer?>(null) }
    var pageIndex by remember { mutableIntStateOf(0) }
    var pageBitmap by remember { mutableStateOf<Bitmap?>(null) }

    LaunchedEffect(bookId) {
        book = container.libraryRepository.getBook(bookId)
    }

    DisposableEffect(book) {
        val currentBook = book
        var fd: ParcelFileDescriptor? = null
        if (currentBook != null) {
            val file = copyAssetToCache(context, currentBook.assetPath)
            fd = ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
            renderer = PdfRenderer(fd)
        }
        onDispose {
            renderer?.close()
            fd?.close()
        }
    }

    LaunchedEffect(renderer, pageIndex) {
        val current = renderer ?: return@LaunchedEffect
        if (pageIndex !in 0 until current.pageCount) return@LaunchedEffect
        val rendered = withContext(Dispatchers.IO) {
            current.openPage(pageIndex).use { page ->
                val bitmap = Bitmap.createBitmap(page.width * 2, page.height * 2, Bitmap.Config.ARGB_8888)
                page.render(bitmap, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                bitmap
            }
        }
        pageBitmap = rendered
    }

    Column(Modifier.fillMaxSize().background(SultanColors.RoyalNavyDeep)) {
        Row(
            Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                book?.titleEn ?: "",
                style = MaterialTheme.typography.titleMedium,
                color = SultanColors.Platinum,
                modifier = Modifier.weight(1f)
            )
            IconButton(onClick = { /* note-taking hook: container.libraryRepository.addNote(...) */ }) {
                Icon(Icons.Filled.EditNote, contentDescription = "Add note", tint = SultanColors.RoyalGold)
            }
            IconButton(onClick = { /* bookmark hook: container.libraryRepository.addBookmark(...) */ }) {
                Icon(Icons.Filled.BookmarkBorder, contentDescription = "Bookmark", tint = SultanColors.RoyalGold)
            }
        }

        Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
            pageBitmap?.let { bmp ->
                Image(bitmap = bmp.asImageBitmap(), contentDescription = "Page ${pageIndex + 1}")
            }
        }

        Row(
            Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            IconButton(onClick = { if (pageIndex > 0) pageIndex-- }) {
                Icon(Icons.Filled.ChevronLeft, contentDescription = "Previous page", tint = SultanColors.RoyalGold)
            }
            Text(
                "Page ${pageIndex + 1} of ${renderer?.pageCount ?: 0}",
                color = SultanColors.Silver,
                style = MaterialTheme.typography.bodyMedium
            )
            IconButton(onClick = { val count = renderer?.pageCount ?: 0; if (pageIndex < count - 1) pageIndex++ }) {
                Icon(Icons.Filled.ChevronRight, contentDescription = "Next page", tint = SultanColors.RoyalGold)
            }
        }
    }
}

private fun copyAssetToCache(context: Context, assetPath: String): File {
    val outFile = File(context.cacheDir, assetPath.replace("/", "_"))
    if (!outFile.exists()) {
        context.assets.open(assetPath).use { input ->
            FileOutputStream(outFile).use { output -> input.copyTo(output) }
        }
    }
    return outFile
}
