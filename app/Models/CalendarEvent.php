<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CalendarEvent extends Model
{
    use HasFactory;

    protected $fillable = [
        'related_type',
        'related_id',
        'title',
        'start_at',
        'end_at',
        'color',
        'reminder_days',
    ];

    protected $casts = [
        'start_at' => 'datetime',
        'end_at' => 'datetime',
        'reminder_days' => 'array',
    ];
}
