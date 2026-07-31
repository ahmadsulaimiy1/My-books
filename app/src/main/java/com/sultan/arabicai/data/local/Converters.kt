package com.sultan.arabicai.data.local

import androidx.room.TypeConverter
import com.sultan.arabicai.data.local.entity.BookFormat
import com.sultan.arabicai.data.local.entity.CertificateLevel
import com.sultan.arabicai.data.local.entity.ProficiencyLevel
import com.sultan.arabicai.data.local.entity.QuizDifficulty
import com.sultan.arabicai.data.local.entity.QuizType

/** Room has no built-in enum support; every enum column round-trips through its name. */
class Converters {
    @TypeConverter
    fun fromBookFormat(value: BookFormat): String = value.name

    @TypeConverter
    fun toBookFormat(value: String): BookFormat = BookFormat.valueOf(value)

    @TypeConverter
    fun fromProficiencyLevel(value: ProficiencyLevel): String = value.name

    @TypeConverter
    fun toProficiencyLevel(value: String): ProficiencyLevel = ProficiencyLevel.valueOf(value)

    @TypeConverter
    fun fromQuizType(value: QuizType): String = value.name

    @TypeConverter
    fun toQuizType(value: String): QuizType = QuizType.valueOf(value)

    @TypeConverter
    fun fromQuizDifficulty(value: QuizDifficulty): String = value.name

    @TypeConverter
    fun toQuizDifficulty(value: String): QuizDifficulty = QuizDifficulty.valueOf(value)

    @TypeConverter
    fun fromCertificateLevel(value: CertificateLevel): String = value.name

    @TypeConverter
    fun toCertificateLevel(value: String): CertificateLevel = CertificateLevel.valueOf(value)
}

/** Helper for the pipe-delimited [com.sultan.arabicai.data.local.entity.QuizQuestionEntity.options] column. */
fun String.toOptionList(): List<String> = if (isBlank()) emptyList() else split("|")
fun List<String>.toOptionsColumn(): String = joinToString("|")
