package com.sultan.arabicai.certificate

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.Typeface
import android.graphics.pdf.PdfDocument
import com.google.zxing.BarcodeFormat
import com.google.zxing.qrcode.QRCodeWriter
import com.sultan.arabicai.data.local.entity.CertificateEntity
import com.sultan.arabicai.data.local.entity.CertificateLevel
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID
import kotlin.random.Random

/**
 * Renders a luxury A4-landscape certificate as a real, openable PDF using the platform
 * [PdfDocument] API (no external PDF dependency) and embeds a QR code — generated locally
 * with ZXing, no network call — that encodes a verification code checkable against the
 * `certificates` table (see [com.sultan.arabicai.data.local.dao.CertificateDao.getByVerificationCode]).
 * Cloud-hosted verification (a public URL a third party could scan) is a Phase-2 item once a
 * backend exists; today the QR content is the same code shown printed on the certificate, so
 * verification works fully offline within the app.
 */
object CertificateGenerator {

    private const val PAGE_WIDTH = 1600
    private const val PAGE_HEIGHT = 1131 // A4 landscape ratio

    private val NAVY = Color.parseColor("#082A66")
    private val NAVY_DEEP = Color.parseColor("#051A40")
    private val GOLD = Color.parseColor("#C9A961")
    private val GOLD_BRIGHT = Color.parseColor("#E4C77E")
    private val PLATINUM = Color.parseColor("#E8E9EC")

    fun newVerificationCode(): String =
        "SAAI-" + UUID.randomUUID().toString().take(8).uppercase(Locale.US) + "-" + Random.nextInt(1000, 9999)

    fun levelTitle(level: CertificateLevel): Pair<String, String> = when (level) {
        CertificateLevel.COURSE_COMPLETION -> "Certificate of Course Completion" to "شهادة إتمام الدورة"
        CertificateLevel.EXCELLENCE -> "Certificate of Excellence" to "شهادة التميز"
        CertificateLevel.DISTINCTION -> "Certificate of Distinction" to "شهادة الامتياز"
        CertificateLevel.HONOUR -> "Certificate of Honour" to "شهادة الشرف"
        CertificateLevel.GRAND_HONOUR -> "Grand Honour Certificate" to "شهادة الشرف الكبرى"
    }

    fun generate(context: Context, certificate: CertificateEntity): File {
        val document = PdfDocument()
        val pageInfo = PdfDocument.PageInfo.Builder(PAGE_WIDTH, PAGE_HEIGHT, 1).create()
        val page = document.startPage(pageInfo)
        val canvas = page.canvas

        drawBackground(canvas)
        drawBorder(canvas)
        drawSeal(canvas)
        drawTitleBlock(canvas, certificate)
        drawQrBlock(canvas, certificate)
        drawFooter(canvas, certificate)

        document.finishPage(page)

        val outDir = File(context.filesDir, "certificates").apply { mkdirs() }
        val outFile = File(outDir, "certificate_${certificate.verificationCode}.pdf")
        FileOutputStream(outFile).use { document.writeTo(it) }
        document.close()
        return outFile
    }

    private fun drawBackground(canvas: Canvas) {
        val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = NAVY }
        canvas.drawRect(0f, 0f, PAGE_WIDTH.toFloat(), PAGE_HEIGHT.toFloat(), paint)

        // Diagonal deep-navy accent panel, echoing the launcher motif.
        val accentPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = NAVY_DEEP }
        val path = android.graphics.Path().apply {
            moveTo(0f, PAGE_HEIGHT.toFloat())
            lineTo(0f, PAGE_HEIGHT * 0.6f)
            lineTo(PAGE_WIDTH * 0.35f, PAGE_HEIGHT.toFloat())
            close()
        }
        canvas.drawPath(path, accentPaint)
    }

    private fun drawBorder(canvas: Canvas) {
        val outer = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = GOLD
            style = Paint.Style.STROKE
            strokeWidth = 6f
        }
        val inner = Paint(outer).apply { strokeWidth = 2f }
        val margin = 48f
        canvas.drawRect(RectF(margin, margin, PAGE_WIDTH - margin, PAGE_HEIGHT - margin), outer)
        canvas.drawRect(
            RectF(margin + 16f, margin + 16f, PAGE_WIDTH - margin - 16f, PAGE_HEIGHT - margin - 16f),
            inner
        )
    }

    private fun drawSeal(canvas: Canvas) {
        val cx = PAGE_WIDTH / 2f
        val cy = 190f
        val outerRadius = 70f
        val innerRadius = 30f
        val path = android.graphics.Path()
        for (i in 0 until 16) {
            val angleDeg = -90.0 + i * 22.5
            val radius = if (i % 2 == 0) outerRadius else innerRadius
            val angleRad = Math.toRadians(angleDeg)
            val x = cx + radius * kotlin.math.cos(angleRad).toFloat()
            val y = cy + radius * kotlin.math.sin(angleRad).toFloat()
            if (i == 0) path.moveTo(x, y) else path.lineTo(x, y)
        }
        path.close()

        val sealPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = GOLD }
        canvas.drawPath(path, sealPaint)
        canvas.drawCircle(cx, cy, 18f, Paint(Paint.ANTI_ALIAS_FLAG).apply { color = NAVY })
    }

    private fun drawTitleBlock(canvas: Canvas, certificate: CertificateEntity) {
        val centerX = PAGE_WIDTH / 2f

        val kicker = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = GOLD_BRIGHT
            textSize = 26f
            textAlign = Paint.Align.CENTER
            typeface = Typeface.create(Typeface.SERIF, Typeface.NORMAL)
        }
        canvas.drawText("SULTAN ARABIC AI  •  SAUDI VISION 2030 FLAGSHIP EDITION", centerX, 320f, kicker)

        val titlePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = PLATINUM
            textSize = 64f
            textAlign = Paint.Align.CENTER
            typeface = Typeface.create(Typeface.SERIF, Typeface.BOLD)
        }
        canvas.drawText(certificate.titleEn, centerX, 410f, titlePaint)

        val titleArPaint = Paint(titlePaint).apply { textSize = 46f }
        canvas.drawText(certificate.titleAr, centerX, 480f, titleArPaint)

        val presentedTo = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = Color.parseColor("#B9BDC7")
            textSize = 28f
            textAlign = Paint.Align.CENTER
        }
        canvas.drawText("This is presented to", centerX, 570f, presentedTo)

        val namePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = GOLD
            textSize = 56f
            textAlign = Paint.Align.CENTER
            typeface = Typeface.create(Typeface.SERIF, Typeface.BOLD)
        }
        canvas.drawText(certificate.recipientName, centerX, 650f, namePaint)

        val underline = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = GOLD
            strokeWidth = 2f
        }
        canvas.drawLine(centerX - 260f, 675f, centerX + 260f, 675f, underline)

        val body = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = PLATINUM
            textSize = 24f
            textAlign = Paint.Align.CENTER
        }
        canvas.drawText(
            "in recognition of outstanding achievement within the SULTAN Arabic curriculum",
            centerX, 730f, body
        )
    }

    private fun drawQrBlock(canvas: Canvas, certificate: CertificateEntity) {
        val qrSize = 190
        val qrBitmap = generateQrBitmap(certificate.verificationCode, qrSize)
        val left = PAGE_WIDTH - 320f
        val top = PAGE_HEIGHT - 340f

        val frame = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = PLATINUM }
        canvas.drawRoundRect(RectF(left - 16f, top - 16f, left + qrSize + 16f, top + qrSize + 16f), 12f, 12f, frame)
        canvas.drawBitmap(qrBitmap, left, top, null)

        val label = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = Color.parseColor("#B9BDC7")
            textSize = 18f
            textAlign = Paint.Align.CENTER
        }
        canvas.drawText("Verify: ${certificate.verificationCode}", left + qrSize / 2f, top + qrSize + 44f, label)
    }

    private fun drawFooter(canvas: Canvas, certificate: CertificateEntity) {
        val dateFormat = SimpleDateFormat("d MMMM yyyy", Locale.ENGLISH)
        val dateText = dateFormat.format(Date(certificate.issuedAtEpochMillis))

        val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = Color.parseColor("#B9BDC7")
            textSize = 22f
        }
        canvas.drawText("Issued $dateText", 130f, PAGE_HEIGHT - 130f, paint)
        canvas.drawText("Digitally signed • SULTAN Hanafi Royal Schools", 130f, PAGE_HEIGHT - 100f, paint)
    }

    private fun generateQrBitmap(content: String, sizePx: Int): Bitmap {
        val matrix = QRCodeWriter().encode(content, BarcodeFormat.QR_CODE, sizePx, sizePx)
        val bitmap = Bitmap.createBitmap(sizePx, sizePx, Bitmap.Config.RGB_565)
        for (x in 0 until sizePx) {
            for (y in 0 until sizePx) {
                bitmap.setPixel(x, y, if (matrix.get(x, y)) Color.BLACK else Color.WHITE)
            }
        }
        return bitmap
    }
}
