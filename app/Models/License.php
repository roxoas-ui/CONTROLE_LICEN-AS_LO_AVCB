<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class License extends Model
{
    use HasFactory;

    protected $fillable = [
        'project_id',
        'number',
        'issuer',
        'issued_at',
        'expires_at',
        'type',
        'status',
        'metadata',
    ];

    protected $casts = [
        'metadata' => 'array',
        'issued_at' => 'date',
        'expires_at' => 'date',
    ];

    public function project()
    {
        return $this->belongsTo(Project::class);
    }

    public function conditionals()
    {
        return $this->hasMany(Conditional::class);
    }

    public function attachments()
    {
        return $this->morphMany(Attachment::class, 'attachable');
    }
}
