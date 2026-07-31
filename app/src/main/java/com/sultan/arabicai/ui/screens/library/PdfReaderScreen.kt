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
import androidx.compose.material.icons.automirrored.filled.NavigateBefore
import androidx.compose.material.icons.automirrored.filled.NavigateNext
import androidx.compose.material.icons.filled.BookmarkBorder
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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
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
 *
 * Opening the book (asset copy + PdfRenderer construction) and rendering each page both run on
 * [Dispatchers.IO] via [LaunchedEffect] — none of it runs synchronously on the main thread.
 */
@Composable
fun PdfReaderScreen(bookId: Long) {
    val container = LocalAppContainer.current
    val context = LocalContext.current

    var book by remember { mutableStateOf<com.sultan.arabicai.data.local.entity.BookEntity?>(null) }
    var renderer by remember { mutableStateOf<PdfRenderer?>(null) }
    var pfd by remember { mutableStateOf<ParcelFileDescriptor?>(null) }
    var loadError by remember { mutableStateOf(false) }
    var pageIndex by remember { mutableIntStateOf(0) }
    var pageBitmap by remember { mutableStateOf<Bitmap?>(null) }

    LaunchedEffect(bookId) {
        book = container.libraryRepository.getBook(bookId)
    }

    // Opening the book is real disk I/O (asset copy + PdfRenderer construction) — always off
    // the main thread, and guarded so a corrupt/missing asset surfaces as an error state
    // instead of crashing the screen.
    LaunchedEffect(book) {
        val currentBook = book ?: return@LaunchedEffect
        val opened = withContext(Dispatchers.IO) {
            runCatching {
                val file = copyAssetToCache(context, currentBook.assetPath)
                val descriptor = ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
                descriptor to PdfRenderer(descriptor)
            }
        }
        opened.onSuccess { (descriptor, r) ->
            pfd = descriptor
            renderer = r
        }.onFailure {
            loadError = true
        }
    }

    // Cleanup runs once, when the screen itself leaves composition — reads whichever
    // renderer/descriptor are current at that point, not whatever existed when this effect
    // was installed.
    DisposableEffect(Unit) {
        onDispose {
            renderer?.close()
            pfd?.close()
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
                Icon(Icons.Filled.EditNote, contentDescription = stringResource(R.string.pdf_reader_add_note), tint = SultanColors.RoyalGold)
            }
            IconButton(onClick = { /* bookmark hook: container.libraryRepository.addBookmark(...) */ }) {
                Icon(Icons.Filled.BookmarkBorder, contentDescription = stringResource(R.string.pdf_reader_bookmark), tint = SultanColors.RoyalGold)
            }
        }

        Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
            when {
                loadError -> Text(
                    stringResource(R.string.pdf_reader_load_error),
                    color = SultanColors.Silver,
                    style = MaterialTheme.typography.bodyMedium
                )
                pageBitmap != null -> Image(
                    bitmap = pageBitmap!!.asImageBitmap(),
                    contentDescription = stringResource(R.string.pdf_reader_page_content_description, pageIndex + 1)
                )
            }
        }

        Row(
            Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            IconButton(onClick = { if (pageIndex > 0) pageIndex-- }) {
                // AutoMirrored so the arrow points the correct direction in RTL layouts too.
                Icon(Icons.AutoMirrored.Filled.NavigateBefore, contentDescription = stringResource(R.string.pdf_reader_previous_page), tint = SultanColors.RoyalGold)
            }
            Text(
                stringResource(R.string.pdf_reader_page_indicator, pageIndex + 1, renderer?.pageCount ?: 0),
                color = SultanColors.Silver,
                style = MaterialTheme.typography.bodyMedium
            )
            IconButton(onClick = { val count = renderer?.pageCount ?: 0; if (pageIndex < count - 1) pageIndex++ }) {
                Icon(Icons.AutoMirrored.Filled.NavigateNext, contentDescription = stringResource(R.string.pdf_reader_next_page), tint = SultanColors.RoyalGold)
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
