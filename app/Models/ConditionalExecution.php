<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ConditionalExecution extends Model
{
    use HasFactory;

    protected $fillable = [
        'conditional_id',
        'executed_by',
        'executed_at',
        'status',
        'evidence_attachment_id',
        'notes',
    ];

    protected $casts = [
        'executed_at' => 'datetime',
    ];

    public function conditional()
    {
        return $this->belongsTo(Conditional::class);
    }
}
